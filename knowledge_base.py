# knowledge_base.py: Loads and manages the content from the lesson file.

import os
import random
import re
import config

# Global variable to store the loaded concepts
_KNOWLEDGE_BASE = []

def load_and_parse_kb(file_path):
    """
    Loads a text file and parses it into a list of dictionaries.
    """
    if not os.path.exists(file_path):
        print(f"Error: Knowledge base file not found at '{file_path}'")
        return []
        
    knowledge_base = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to find Topic/Answer blocks.
    pattern = re.compile(r"Topic:\s*(.*?)\s*Answer:\s*(.*?)(?=\s*Topic:|\Z)", re.DOTALL | re.IGNORECASE)
    
    matches = pattern.findall(content)
    
    for match in matches:
        concept = match[0].strip()
        description = match[1].strip()
        if concept and description:
            knowledge_base.append({"concept": concept, "description": description})
            
    if not knowledge_base:
        print("Warning: Could not parse any topics from the lesson file. Check the format.")
        
    return knowledge_base

def load_kb():
    """
    Loads the knowledge base from the file specified in config.
    """
    global _KNOWLEDGE_BASE
    kb_path = getattr(config, 'KB_FILE_PATH', 'LessonAILiteracy.txt')
    _KNOWLEDGE_BASE = load_and_parse_kb(kb_path)
    

def get_concept_list():
    """Returns a list of all concept names (topics)."""
    return [item["concept"] for item in _KNOWLEDGE_BASE]

def get_ground_truth(concept_name):
    """Finds a concept by its name and returns its description."""
    for item in _KNOWLEDGE_BASE:
        if item["concept"].lower() == concept_name.lower():
            return item["description"]
    return f"No ground truth found for concept: {concept_name}"

def get_random_question(asked_indices):
    """Selects a random, unasked question from the loaded knowledge base."""
    global _KNOWLEDGE_BASE

    if not _KNOWLEDGE_BASE:
        print("Error: get_random_question called but _KNOWLEDGE_BASE is empty.")
        return None, None, -1

    available_indices = [i for i, _ in enumerate(_KNOWLEDGE_BASE) if i not in asked_indices]

    if not available_indices:
        # All questions have been asked
        return None, None, -1

    random_index = random.choice(available_indices)
    item = _KNOWLEDGE_BASE[random_index]

    return item.get('concept'), item.get('description'), random_index
