# Sagafy

A psychology-based application that helps users document their professional experiences in detail, creating comprehensive work history records for resumes, cover letters, and interview preparation.

## Features

- **Psychological Framework**: Uses research-validated memory enhancement techniques to uncover detailed work experiences
- **Guided Conversation**: AI-powered questioning guides users through five specialized sections
- **Document Generation**: Creates polished professional documentation from user responses
- **User Authentication**: Secure login and registration system
- **Session Management**: Save and continue multiple work history sessions

## Psychological Framework

This tool uses a structured, research-backed approach to documentation:

1. **Context Reinstatement**: Recreates the mental and physical context of the work environment
2. **Free Narrative**: Encourages chronological storytelling of experiences
3. **Structured Probing**: Explores technical, interpersonal, and organizational domains
4. **Identity Development**: Reflects on professional growth and impact
5. **Quantitative Integration**: Measures achievements with concrete metrics

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **AI**: OpenAI GPT-4 API
- **NLP**: SpaCy

## Setup Instructions

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/Tplhardy/Sagafy.git
   cd work-history-tool
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Download SpaCy language model:
   ```
   python -m spacy download en_core_web_sm
   ```

5. Create environment variables file:
   ```
   cp .env.example .env
   ```
   Then edit `.env` with your OpenAI API key and a secret key for Flask.

### Running the Application

1. Start the Flask development server:
   ```
   flask run
   ```

2. Open a web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Project Structure

```
work-history-tool/
├── app.py                  # Main Flask application
├── utils/                  # Utility modules
│   ├── ai.py               # OpenAI integration
│   ├── db.py               # Database functions
│   └── sections.py         # Psychological framework
├── models/                 # Data models
│   ├── user.py             # User model
│   └── session.py          # Session model
├── static/                 # Static assets
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript
│   └── img/                # Images
├── templates/              # HTML templates
├── .env                    # Environment variables
└── requirements.txt        # Project dependencies
```

## Usage

1. Create an account or log in
2. Start a new work history session for a specific job or role
3. Answer the AI-guided questions about your experience
4. Progress through all framework sections
5. Generate and download your work history document

## Deployment

For production deployment:

1. Set `FLASK_ENV=production` in your `.env` file
2. Use a production-ready WSGI server:
   ```
   gunicorn app:app
   ```
3. Set a strong `SECRET_KEY` in your environment variables

## License

[MIT License](LICENSE)

## Acknowledgements

- Psychological framework based on research by Riggenbach, Gronlund, and Zoladz (2024)
- OpenAI for providing the GPT-4 API
