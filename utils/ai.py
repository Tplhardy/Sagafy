"""
AI utilities for generating questions and summaries
"""
import os
import openai
import json
from .sections import get_section_display_name

# Initialize OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Define system prompts for each section
SECTION_PROMPTS = {
    "context_reinstatement": """
You are an expert interviewer conducting a Context Reinstatement phase of a psychological interview about work history.

Your goal is to help the user recall their work environment in vivid detail. Research shows that environmental context reinstatement helps unlock detailed memories.

Focus on:
- Physical workspace details (desk, office layout, building)
- Daily routines and patterns
- Sensory details (sounds, sights, feelings)
- Interpersonal dynamics (colleagues, team structure)

Ask one specific question at a time. Build on their previous answers to explore the environment more deeply.
Avoid generic questions. Use their specific details to probe further.

IMPORTANT:
- Ask only about contextual/environmental aspects in this phase
- Don't rush to ask about specific projects or achievements yet
- Help them recreate their work environment mentally
- Never repeat the exact same question
- Don't ask more than one question at a time
""",

    "free_narrative": """
You are an expert interviewer conducting a Free Narrative phase of a psychological interview about work history.

Your goal is to help the user construct a chronological narrative of their work experience. Research shows that free narrative techniques help people recall events in sequence.

Focus on:
- Chronological progression (beginning to end)
- Key milestones and turning points
- Critical incidents and significant events
- Natural story flow

Ask one specific question at a time. Build on their previous answers to help them tell their story in sequence.
Avoid jumping around in time. Focus on helping them move through their experience chronologically.

IMPORTANT:
- Let them tell their story without excessive interruption
- Guide them from beginning to end of their experience
- Use temporal markers (then, next, after that)
- Never repeat the exact same question
- Don't ask more than one question at a time
""",

    "structured_probing": """
You are an expert interviewer conducting a Structured Probing phase of a psychological interview about work history.

Your goal is to systematically explore specific domains of their work experience. Research shows that structured domain exploration uncovers important details.

Focus on these domains (explore each thoroughly):
- Technical domain (skills, tools, processes)
- Interpersonal domain (teamwork, leadership, communication)
- Organizational domain (impact, initiatives, improvements)

Ask one specific question at a time. Build on their previous answers to probe more deeply into each domain.
Be methodical in your questioning to ensure comprehensive coverage.

IMPORTANT:
- Ensure you explore all three domains (technical, interpersonal, organizational)
- Ask for specific examples with concrete details
- Follow up on mentions of skills, challenges, or achievements
- Never repeat the exact same question
- Don't ask more than one question at a time
""",

    "identity_development": """
You are an expert interviewer conducting an Identity Development phase of a psychological interview about work history.

Your goal is to help the user reflect on their professional growth and impact. Research shows that self-reflection enhances memory recall and meaning-making.

Focus on:
- Personal growth trajectory
- Skill development and learning
- Self-perception changes
- Impact assessment (on others, organization, field)

Ask one specific question at a time. Build on their previous answers to deepen reflection.
Encourage them to consider how this experience shaped them professionally.

IMPORTANT:
- Focus on reflection rather than just factual recall
- Connect their experience to their professional identity
- Explore how they changed and grew
- Never repeat the exact same question
- Don't ask more than one question at a time
""",

    "quantitative_integration": """
You are an expert interviewer conducting a Quantitative Integration phase of a psychological interview about work history.

Your goal is to help the user quantify their achievements and impact. Research shows that specific metrics strengthen resume content.

Focus on:
- Performance indicators and metrics
- Comparative measures (before/after, benchmarks)
- Resource management (time, budget, team size)
- Concrete achievements in numbers

Ask one specific question at a time. Build on their previous answers to identify quantifiable elements.
Help them translate their experience into measurable achievements.

IMPORTANT:
- Focus on specific numbers and percentages
- Help them quantify previously mentioned achievements
- Ask about scales, scope, and measurable impact
- Never repeat the exact same question
- Don't ask more than one question at a time
""",

    "complete": """
You are an expert interviewer who has completed a comprehensive psychological interview about work history.

Your goal is to acknowledge the completion and encourage the user to review their documentation.

IMPORTANT:
- Thank them for their detailed responses
- Explain that the session is complete
- Encourage them to review and use their documented work history
"""
}

def generate_question(user_input, message_history, section):
    """
    Generate the next question based on conversation history and current section
    
    Args:
        user_input: The latest user input
        message_history: List of previous messages
        section: Current psychological framework section
        
    Returns:
        AI-generated question as a string
    """
    # If session is complete, return completion message
    if section == "complete":
        return ("Thank you for completing your work history documentation. You can now generate "
                "a comprehensive summary of your experience that can be used for resumes, cover letters, "
                "and interview preparation.")
    
    # Get the appropriate system prompt for the current section
    system_prompt = SECTION_PROMPTS.get(section, SECTION_PROMPTS["context_reinstatement"])
    
    # Format section name for display
    section_display = get_section_display_name(section)
    
    # Add section header to system prompt
    system_prompt = f"[{section_display} Phase]\n\n" + system_prompt
    
    # Prepare messages for API call
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add relevant conversation history (last 8 messages maximum)
    # This helps maintain context without exceeding token limits
    relevant_history = message_history[-8:] if len(message_history) > 8 else message_history
    messages.extend(relevant_history)
    
    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Use appropriate model
            messages=messages,
            temperature=0.7,
            max_tokens=200,
            top_p=0.95,
            frequency_penalty=0.5,
            presence_penalty=0.5
        )
        
        # Get the generated response
        question = response.choices[0].message.content.strip()
        
        # Check for simple error cases
        if len(question) < 5:
            return "Could you tell me more about your experience in this role?"
        
        return question
        
    except Exception as e:
        print(f"Error generating question: {e}")
        
        # Fallback responses based on section
        fallbacks = {
            "context_reinstatement": "Could you describe your physical workspace in more detail?",
            "free_narrative": "What happened next in your work journey?",
            "structured_probing": "Can you share a specific example of a technical challenge you faced?",
            "identity_development": "How did this experience change you professionally?",
            "quantitative_integration": "Are there any metrics or numbers you can share about your impact?"
        }
        
        return fallbacks.get(section, "Could you tell me more about your experience?")

def generate_section_summary(section_name, content):
    """
    Generate a professional summary of a section for the final document
    
    Args:
        section_name: The name of the section
        content: List of user responses in this section
        
    Returns:
        Summarized content as a string
    """
    # Format section name for display
    section_display = get_section_display_name(section_name)
    
    # Combine all user content
    combined_content = "\n\n".join(content)
    
    # System prompts for different sections
    summary_prompts = {
        "context_reinstatement": "Extract key details about the work environment and context.",
        "free_narrative": "Create a chronological narrative of their work experience.",
        "structured_probing": "Highlight key technical skills, interpersonal abilities, and organizational impact.",
        "identity_development": "Summarize professional growth and development.",
        "quantitative_integration": "Emphasize quantifiable achievements and metrics."
    }
    
    # Default prompt if section not found
    section_specific_prompt = summary_prompts.get(
        section_name, 
        "Extract key professional details from this content."
    )
    
    # Create the system prompt
    system_prompt = f"""
    You are an expert resume writer. Transform the following interview responses into polished, 
    professional content for a work history document.
    
    Section: {section_display}
    
    {section_specific_prompt}
    
    Focus on:
    - Professional language and tone
    - Accomplishment-focused statements
    - Relevant skills and experiences
    - Concrete details and examples
    
    Format with appropriate paragraph breaks. Use bullet points for key achievements if appropriate.
    Maintain first-person perspective but enhance the language for professional impact.
    """
    
    # Prepare messages for API call
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": combined_content}
    ]
    
    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Use appropriate model
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Get the generated response
        summary = response.choices[0].message.content.strip()
        
        return summary
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        
        # Fallback: return original content with a note
        return f"**Note: Automatic summary generation failed. Below is the original content:**\n\n{combined_content}"
