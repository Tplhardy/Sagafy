import os
from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import json

# Import utility modules
from utils.ai import generate_question, generate_section_summary
from utils.db import get_db_connection, init_db
from utils.sections import get_next_section, check_section_completion
from models.user import User
from models.session import WorkSession

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if user:
        return User(user['id'], user['username'])
    return None

@app.before_first_request
def setup():
    init_db()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user:
            flash('Username already exists.')
            return redirect(url_for('register'))
            
        conn.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        conn.commit()
        conn.close()
        
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
            
        flash('Invalid username or password')
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    sessions = conn.execute(
        'SELECT * FROM sessions WHERE user_id = ? ORDER BY updated_at DESC',
        (current_user.id,)
    ).fetchall()
    conn.close()
    
    return render_template('dashboard.html', sessions=sessions)

@app.route('/session/new', methods=['POST'])
@login_required
def new_session():
    title = request.form.get('title', f"Work History - {datetime.now().strftime('%Y-%m-%d')}")
    
    conn = get_db_connection()
    cursor = conn.execute(
        '''INSERT INTO sessions 
           (user_id, title, created_at, updated_at, current_section) 
           VALUES (?, ?, ?, ?, ?)''',
        (current_user.id, title, datetime.now(), datetime.now(), 'context_reinstatement')
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return redirect(url_for('chat', session_id=session_id))

@app.route('/session/<int:session_id>')
@login_required
def chat(session_id):
    conn = get_db_connection()
    
    # Check if session belongs to user
    work_session = conn.execute(
        'SELECT * FROM sessions WHERE id = ? AND user_id = ?',
        (session_id, current_user.id)
    ).fetchone()
    
    if not work_session:
        conn.close()
        flash('Session not found or access denied')
        return redirect(url_for('dashboard'))
    
    # Get messages for this session
    messages = conn.execute(
        'SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp',
        (session_id,)
    ).fetchall()
    
    conn.close()
    
    # Format messages for template
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            'role': msg['role'],
            'content': msg['content'],
            'section': msg['section']
        })
    
    # If no messages, generate the first question
    if not formatted_messages:
        initial_question = generate_question('', [], 'context_reinstatement')
        
        conn = get_db_connection()
        conn.execute(
            '''INSERT INTO messages (session_id, role, content, timestamp, section)
               VALUES (?, ?, ?, ?, ?)''',
            (session_id, 'assistant', initial_question, datetime.now(), 'context_reinstatement')
        )
        conn.commit()
        conn.close()
        
        formatted_messages.append({
            'role': 'assistant',
            'content': initial_question,
            'section': 'context_reinstatement'
        })
    
    return render_template(
        'chat.html', 
        session_id=session_id, 
        title=work_session['title'],
        messages=formatted_messages,
        current_section=work_session['current_section']
    )

@app.route('/api/message', methods=['POST'])
@login_required
def send_message():
    data = request.json
    session_id = data.get('session_id')
    user_input = data.get('message', '')
    
    if not session_id or not user_input:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    conn = get_db_connection()
    
    # Check if session belongs to user
    work_session = conn.execute(
        'SELECT * FROM sessions WHERE id = ? AND user_id = ?',
        (session_id, current_user.id)
    ).fetchone()
    
    if not work_session:
        conn.close()
        return jsonify({'error': 'Session not found or access denied'}), 404
    
    current_section = work_session['current_section']
    
    # If session is complete, don't process more messages
    if current_section == 'complete':
        conn.close()
        return jsonify({
            'message': 'This work history session is complete. You can now generate your document.',
            'section': 'complete'
        })
    
    # Get message history
    messages = conn.execute(
        'SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp',
        (session_id,)
    ).fetchall()
    
    # Format message history for AI
    message_history = []
    for msg in messages:
        message_history.append({
            'role': msg['role'],
            'content': msg['content']
        })
    
    # Add user message to history
    message_history.append({
        'role': 'user',
        'content': user_input
    })
    
    # Save user message to database
    conn.execute(
        '''INSERT INTO messages (session_id, role, content, timestamp, section)
           VALUES (?, ?, ?, ?, ?)''',
        (session_id, 'user', user_input, datetime.now(), current_section)
    )
    conn.commit()
    
    # Check if section should be completed
    next_section = check_section_completion(message_history, current_section)
    
    # If section is complete, update session
    if next_section != current_section:
        conn.execute(
            'UPDATE sessions SET current_section = ?, updated_at = ? WHERE id = ?',
            (next_section, datetime.now(), session_id)
        )
        conn.commit()
        current_section = next_section
    
    # Generate AI response
    ai_message = generate_question(user_input, message_history, current_section)
    
    # Save AI message to database
    conn.execute(
        '''INSERT INTO messages (session_id, role, content, timestamp, section)
           VALUES (?, ?, ?, ?, ?)''',
        (session_id, 'assistant', ai_message, datetime.now(), current_section)
    )
    
    # Update session timestamp
    conn.execute(
        'UPDATE sessions SET updated_at = ? WHERE id = ?',
        (datetime.now(), session_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': ai_message,
        'section': current_section
    })

@app.route('/session/<int:session_id>/document')
@login_required
def view_document(session_id):
    conn = get_db_connection()
    
    # Check if session belongs to user
    work_session = conn.execute(
        'SELECT * FROM sessions WHERE id = ? AND user_id = ?',
        (session_id, current_user.id)
    ).fetchone()
    
    if not work_session:
        conn.close()
        flash('Session not found or access denied')
        return redirect(url_for('dashboard'))
    
    # Get messages for this session
    messages = conn.execute(
        'SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp',
        (session_id,)
    ).fetchall()
    
    conn.close()
    
    # Group messages by section
    sections = {}
    for msg in messages:
        section = msg['section']
        if section not in sections:
            sections[section] = []
        
        if msg['role'] == 'user':
            sections[section].append(msg['content'])
    
    # Generate summary for each section
    document_sections = []
    
    for section_name, content in sections.items():
        if section_name != 'complete':  # Skip 'complete' section
            summary = generate_section_summary(section_name, content)
            section_title = section_name.replace('_', ' ').title()
            document_sections.append({
                'title': section_title,
                'content': summary
            })
    
    return render_template('document.html', 
                          title=work_session['title'], 
                          sections=document_sections,
                          session_id=session_id)

@app.route('/session/<int:session_id>/download')
@login_required
def download_document(session_id):
    # Similar to view_document but generates a downloadable file
    # This could be implemented with a library like ReportLab for PDF generation
    pass

if __name__ == '__main__':
    app.run(debug=True)