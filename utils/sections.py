"""
Utility functions for managing the psychological framework sections
"""

# Define the section sequence
SECTIONS = [
    "context_reinstatement",
    "free_narrative",
    "structured_probing",
    "identity_development",
    "quantitative_integration"
]

# Define completion criteria for each section
COMPLETION_CRITERIA = {
    "context_reinstatement": {
        "min_user_messages": 4,
        "required_topics": ["workspace", "office", "desk", "environment", "colleague", "coworker", "team", "routine", "daily"],
        "min_topics": 3,
        "min_total_words": 200
    },
    "free_narrative": {
        "min_user_messages": 4,
        "required_topics": ["first", "begin", "start", "then", "after", "before", "during", "project", "responsibility", "task"],
        "min_topics": 3,
        "min_total_words": 250
    },
    "structured_probing": {
        "min_user_messages": 5,
        "required_topics": ["technical", "skill", "tool", "software", "methodology", "problem", "solution", "challenge", "team", "collaboration"],
        "min_topics": 4,
        "min_total_words": 300
    },
    "identity_development": {
        "min_user_messages": 4,
        "required_topics": ["growth", "learn", "develop", "improve", "change", "progress", "achievement", "proud", "impact", "contribution"],
        "min_topics": 3,
        "min_total_words": 250
    },
    "quantitative_integration": {
        "min_user_messages": 4,
        "required_topics": ["percent", "number", "measure", "increase", "decrease", "improve", "reduce", "budget", "team", "size", "metric"],
        "min_topics": 3,
        "min_total_words": 200
    }
}

def check_section_completion(message_history, current_section):
    """
    Check if the current section is complete and should advance to the next section
    
    Args:
        message_history: List of message dictionaries with 'role' and 'content' keys
        current_section: The current section name
        
    Returns:
        The next section name if complete, otherwise the current section name
    """
    # If already complete, stay complete
    if current_section == "complete":
        return "complete"
    
    # If current section is not in our defined sections, default to first section
    if current_section not in COMPLETION_CRITERIA:
        return SECTIONS[0]
    
    criteria = COMPLETION_CRITERIA[current_section]
    
    # Extract user messages
    user_messages = [msg["content"] for msg in message_history if msg["role"] == "user"]
    
    # Check if minimum number of messages is met
    if len(user_messages) < criteria["min_user_messages"]:
        return current_section
    
    # Combine all user messages for content analysis
    all_content = " ".join(user_messages).lower()
    
    # Check if minimum word count is met
    word_count = len(all_content.split())
    if word_count < criteria["min_total_words"]:
        return current_section
    
    # Check if required topics are covered
    topics_covered = 0
    for topic in criteria["required_topics"]:
        if topic.lower() in all_content:
            topics_covered += 1
    
    if topics_covered < criteria["min_topics"]:
        return current_section
    
    # If all criteria are met, advance to the next section
    return get_next_section(current_section)

def get_next_section(current_section):
    """
    Get the next section in the sequence
    
    Args:
        current_section: The current section name
        
    Returns:
        The next section name, or 'complete' if all sections are complete
    """
    try:
        current_index = SECTIONS.index(current_section)
        if current_index < len(SECTIONS) - 1:
            return SECTIONS[current_index + 1]
        else:
            return "complete"
    except ValueError:
        # If current section is not in the list, default to the first section
        return SECTIONS[0]

def get_section_display_name(section_code):
    """
    Convert section code to display name
    
    Args:
        section_code: The section code (e.g., 'context_reinstatement')
        
    Returns:
        Display name (e.g., 'Context Reinstatement')
    """
    if section_code == "complete":
        return "Complete"
    
    return " ".join(word.capitalize() for word in section_code.split("_"))

def get_section_description(section_code):
    """
    Get the description for a section
    
    Args:
        section_code: The section code
        
    Returns:
        Description of the section
    """
    descriptions = {
        "context_reinstatement": "Recall your work environment, routines, and the people around you.",
        "free_narrative": "Describe your work experience chronologically, from beginning to end.",
        "structured_probing": "Detail specific technical skills, interpersonal challenges, and organizational impact.",
        "identity_development": "Reflect on your professional growth and the impact of this experience.",
        "quantitative_integration": "Quantify your achievements with metrics and comparative measures.",
        "complete": "Your work history documentation is complete."
    }
    
    return descriptions.get(section_code, "")