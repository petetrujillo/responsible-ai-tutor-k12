# tutor.py: Generates helpful hints, remediation, and other tutor-like responses.

from evaluator import get_llm_response

def generate_remediation(concept, ground_truth):
    """Generates a simple explanation for a concept the user struggled with."""
    prompt = f"You are a friendly and encouraging tutor. A student is struggling to understand '{concept}'. Please provide a simple, clear explanation of this concept based on the following information: '{ground_truth}'. Start with a friendly phrase like 'No worries!' or 'Let's break that down.' and keep it concise."
    return get_llm_response(prompt)

def answer_follow_up(concept, user_question):
    """Answers a follow-up question asked by the user."""
    prompt = f"You are a helpful AI Tutor. A student asked a follow-up question about '{concept}'. Their question is: '{user_question}'. Please provide a clear and concise answer to their question."
    return get_llm_response(prompt)

def generate_hint(concept):
    """Generates a subtle hint for the student (used in Easy Mode)."""
    # We ask for a "fun analogy" to make it kid-friendly
    prompt = f"Write a very short, fun hint (under 15 words) for a middle schooler about the concept: '{concept}'. Do NOT give away the definition. Just give a clue or analogy."
    return get_llm_response(prompt)

def generate_fallout_message(concept, time_exceeded, attempts_exceeded):
    """Creates a message for when the fallout handler is triggered."""
    reason = ""
    if time_exceeded:
        reason = "we ran out of time on that one."
    elif attempts_exceeded:
        reason = "we've had a few tries at that one."
    
    message = f"That was a tricky one! No problem, let's move on for now since {reason} We can always come back to the topic of '{concept}' later."
    return message

