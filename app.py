# app.py: Main Flask application for the AI Tutor

from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import time
import config

# Import all necessary functions
from data_logger import setup_local_csv_logging, get_log_payload, log_to_csv, LOGGING_DISABLED
from knowledge_base import load_kb, get_concept_list, get_ground_truth, get_random_question
from tutor import generate_remediation, generate_fallout_message, answer_follow_up, generate_hint
from evaluator import evaluate_answer

# Initialize Flask App
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# --- App Configuration ---
app.config['API_KEY'] = os.environ.get('GEMINI_API_KEY', config.API_KEY)

# --- Session Management ---
user_sessions = {}

# --- Run setup functions ---
setup_local_csv_logging()
load_kb()

def prepare_question_response(concept, ground_truth):
    """Helper to attach a hint if Easy Mode is on."""
    question_text = f"**{concept}**"
    
    # Check Difficulty from Config
    if config.GRADER_DIFFICULTY == 'Easy':
        try:
            # Generate a hint on the fly!
            hint = generate_hint(concept)
            # Clean up the hint text (remove quotes if the AI added them)
            hint = hint.replace('"', '').replace("'", "")
            question_text += f"\n\n*💡 Hint: {hint}*"
        except Exception as e:
            # If hint generation fails for any reason, just show the question
            print(f"Hint generation failed: {e}")
            pass
        
    return question_text

# --- API Routes ---

@app.route('/api/concepts', methods=['GET'])
def get_concepts():
    """Serves the list of concepts for the frontend."""
    concepts = get_concept_list()
    return jsonify(concepts)

@app.route('/api/start', methods=['POST'])
def start_quiz():
    """Starts a new quiz session for a user."""
    data = request.json
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({"error": "Missing session_id."}), 400
    
    # Initialize session state
    user_sessions[session_id] = {
        'asked_indices': [],
        'current_concept': None,
        'current_ground_truth': None,
        'attempts_on_current': 0,
        'start_time_on_current': None
    }
    
    # Get the first question
    concept, ground_truth, index = get_random_question(user_sessions[session_id]['asked_indices'])

    if concept:
        user_sessions[session_id]['asked_indices'].append(index)
        user_sessions[session_id]['current_concept'] = concept
        user_sessions[session_id]['current_ground_truth'] = ground_truth
        user_sessions[session_id]['attempts_on_current'] = 1
        user_sessions[session_id]['start_time_on_current'] = time.time()
        
        response = {
            "evaluation_text": "Let's get started!",
            "remediation_text": "Here is your first question:",
            "sme_answer": "",
            "next_question": prepare_question_response(concept, ground_truth) # Use new helper
        }
        return jsonify(response)
    else:
        return jsonify({"error": "Knowledge base is empty. Cannot start quiz."}), 500


@app.route('/api/ask', methods=['POST'])
def ask():
    """Handles a user's answer to a question."""
    try:
        data = request.json
        session_id = data.get('session_id')
        user_answer = data.get('answer')

        if not session_id or not user_answer:
            return jsonify({"error": "Missing session_id or answer."}), 400

        # --- 1. GET CURRENT SESSION STATE ---
        session_data = user_sessions.get(session_id)
        if not session_data or not session_data.get('current_concept'):
            return jsonify({"error": "Invalid session or no question is active. Please start the quiz."}), 400

        current_concept = session_data['current_concept']
        current_ground_truth = session_data['current_ground_truth']
        
        # --- 2. EVALUATE THE ANSWER ---
        start_time = session_data.get('start_time_on_current', time.time())
        
        evaluation_data = evaluate_answer(
            concept=current_concept,
            ground_truth=current_ground_truth,
            user_answer=user_answer, 
            difficulty=config.GRADER_DIFFICULTY
        )
        
        time_taken = round(time.time() - start_time, 2)
        
        # --- 3. PARSE EVALUATION & HANDLE ERRORS ---
        if 'error' in evaluation_data:
            # If it's a critical API error (not just a glitch), return it
            if "API Key is missing" in evaluation_data['error']:
                 return jsonify({"error": "Error during evaluation.", "details": evaluation_data.get('error')}), 500
            # Otherwise, proceed with safe defaults if keys are missing
            
        scores = evaluation_data.get("scores", {})
        signals = evaluation_data.get("signals", {})
        evaluation_text = evaluation_data.get("evaluation_text", "I received your answer.")
        follow_up_question = evaluation_data.get("follow_up_question", "None")

        final_score = scores.get("final", 0)
        
        response_payload = {
            "evaluation_text": evaluation_text,
            "remediation_text": "",
            "sme_answer": "",
            "next_question": "",
            "scores": scores 
        }

        # --- 4. HANDLE FOLLOW-UP QUESTION ---
        if follow_up_question and follow_up_question.lower() != 'none':
            response_payload["sme_answer"] = answer_follow_up(current_concept, follow_up_question)

        # --- 5. FALLOUT & REMEDIATION LOGIC ---
        time_exceeded = time_taken > config.MAX_TIME_ON_QUESTION
        attempts_exceeded = session_data['attempts_on_current'] >= config.MAX_ATTEMPTS
        passed = final_score >= config.REMEDIATION_THRESHOLD

        fallout_triggered = False

        if not passed and (time_exceeded or attempts_exceeded):
            fallout_triggered = True
            response_payload["remediation_text"] = generate_fallout_message(current_concept, time_exceeded, attempts_exceeded)
            response_payload["sme_answer"] = f"For reference, the key idea for **{current_concept}** was: *{current_ground_truth}*"

        elif not passed:
            session_data['attempts_on_current'] += 1
            response_payload["remediation_text"] = generate_remediation(current_concept, current_ground_truth)
            
            # Instead of just the topic name, we add a friendly bridge.
            # We re-call the helper to ensure the hint is included if needed.
            base_question = prepare_question_response(current_concept, current_ground_truth)
            
            response_payload["next_question"] = f"**Let's give it another shot!**\n\nBased on the explanation above, how would you describe: {base_question}"
            
            if not LOGGING_DISABLED:
                log_payload = get_log_payload(session_id, current_concept, user_answer, scores, signals, time_taken, evaluation_text, fallout_triggered)
                log_to_csv(log_payload)
            
            return jsonify(response_payload) 

        elif passed:
            if response_payload["sme_answer"]:
                response_payload["remediation_text"] = "Great job! I've answered your follow-up question below."
            else:
                response_payload["remediation_text"] = "Well done!"
        
        # --- 6. LOG THE FINAL ATTEMPT ---
        if not LOGGING_DISABLED:
            log_payload = get_log_payload(session_id, current_concept, user_answer, scores, signals, time_taken, evaluation_text, fallout_triggered)
            log_to_csv(log_payload)

        # --- 7. GET NEXT QUESTION ---
        concept, ground_truth, index = get_random_question(session_data['asked_indices'])
        
        if concept:
            session_data['asked_indices'].append(index)
            session_data['current_concept'] = concept
            session_data['current_ground_truth'] = ground_truth
            session_data['attempts_on_current'] = 1
            session_data['start_time_on_current'] = time.time()
            

            response_payload['next_question'] = f"Here is your next question: {prepare_question_response(concept, ground_truth)}"
        else:
            response_payload['next_question'] = "You've completed all the questions! Great job!"
            session_data['current_concept'] = None
        
        return jsonify(response_payload)

    except Exception as e:
        print(f"Error in /ask route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

# --- Frontend Serving Routes ---

@app.route('/')
def index():
    """Serves the main aitutor.html file."""
    return render_template('aitutor.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serves other static files (CSS, JS, images) from the 'static' folder."""
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true')

