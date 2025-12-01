# evaluator.py: Builds prompts, calls the LLM, and parses the evaluation.
import requests
import json
import config

def get_llm_response(prompt, force_json=False):
    """
    Sends a prompt to the Gemini API and returns the text response.
    
    Args:
        prompt (str): The text prompt to send.
        force_json (bool): If True, instructs the API to output strictly valid JSON.
    """
    # Check if API Key is loaded (either from Env Var or settings.ini)
    if not config.API_KEY or config.API_KEY == 'YOUR_GEMINI_API_KEY_HERE':
        return '{"error": "API Key is missing. Check settings.ini or environment variables."}'
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={config.API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    # Basic payload
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    # --- Force JSON Mode ---
    if force_json:
        payload["generationConfig"] = {"response_mime_type": "application/json"}
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        result = response.json()
    
        if 'candidates' in result and result['candidates']:
            content = result['candidates'][0].get('content', {})
            if 'parts' in content and content['parts']:
                return content['parts'][0].get('text', '{"error": "No text part in response"}')
        return '{"error": "Invalid LLM API response format"}'
    except requests.exceptions.HTTPError as e:
        error_details = e.response.text
        print(f"API request failed with details: {error_details}")
        error_payload = {"error": "API request failed", "details": error_details}
        return json.dumps(error_payload)
    except Exception as e:
        print(f"A network or other error occurred: {e}")
        error_payload = {"error": "Network or other error", "details": str(e)}
        return json.dumps(error_payload)

def evaluate_answer(concept, ground_truth, user_answer, difficulty):
    """Evaluates the user's answer and returns a parsed JSON object."""
    
    # --- DIFFICULTY SETTINGS ---
    if difficulty == "Strict":
        system_role = "You are a strict academic professor grading a university exam."
        leniency_instruction = "Deduct points for any missing technical details, lack of precision, or informal language."
    elif difficulty == "Easy":
        system_role = "You are a supportive middle-school tutor."
        leniency_instruction = (
            "EXTREME LENIENCY MODE ENABLED:\n"
            "1. CONTEXT ASSUMPTION: If the student provides a correct GENERAL definition, COUNT IT AS 100% CORRECT.\n"
            "2. NO NITPICKING: Ignore spelling/grammar.\n"
            "3. ENCOURAGEMENT: Focus entirely on what they got RIGHT."
        )
    else: # Normal
        system_role = "You are a fair high-school teacher."
        leniency_instruction = "Balance precision with understanding. Award high points for the core concept, but require some specific details for a perfect score."

    eval_prompt = f"""
**Role:** {system_role}

**Task:** Evaluate a student's answer against a Ground Truth definition.

**Context:**
- Topic: "{concept}"
- Student's Answer: "{user_answer}"
- Ground Truth (Reference Material): "{ground_truth}"
- Grading Mode: "{difficulty}"

**Grading Instructions:**
1. {leniency_instruction}
2. **Correctness (0-50):** How factually accurate is the answer?
3. **Explanation (0-50):** Did they use their own words?
4. **Feedback:** Write a helpful evaluation. Start with the score.
5. **REDUNDANCY BLOCKER (CRITICAL):** - If the student scores less than 30 points OR says "I don't know":
   - **DO NOT** explain the concept in the `evaluation_text`. 
   - **DO NOT** give the definition.
   - ONLY say "Thanks for your honesty" or "Good effort" and mention that a helpful explanation is coming up next. Keep it under 20 words.
   - *Reason:* The system will display a separate Remediation card immediately after this, so your explanation would be repetitive.

**CRITICAL LOGIC FOR FOLLOW-UP QUESTIONS:**
- **Constraint:** If the student is simply answering the quiz question (even incorrectly), set 'follow_up_question' to "None".
- **Prevention:** Do NOT infer a question. If they didn't ask, the value MUST be "None".

**JSON Output Format:**
{{
  "scores": {{
    "correctness": <int>,
    "explanation": <int>,
    "bonus": <0 or 5>,
    "final": <int>
  }},
  "signals": {{
    "correctness_explanation_gap": <bool>,
    "uncertainty_detected": <bool>,
    "persona": "<string>"
  }},
  "evaluation_text": "<string starting with '**Scores: ...**'>",
  "follow_up_question": "<string or 'None'>"
}}
    """
    
    raw_response = get_llm_response(eval_prompt, force_json=True)
    
    try:
        # Attempt to parse the JSON directly
        return json.loads(raw_response)
        
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw output was: {raw_response}")
        
        # --- SAFETY NET ---
        return {
            "scores": {
                "correctness": 0,
                "explanation": 0,
                "bonus": 0,
                "final": 0
            },
            "signals": {
                "correctness_explanation_gap": False,
                "uncertainty_detected": False,
                "persona": "N/A"
            },
            "evaluation_text": "**Technical Glitch:** I had a little trouble reading your answer. Let's try the next one!",
            "follow_up_question": "None"
        }
