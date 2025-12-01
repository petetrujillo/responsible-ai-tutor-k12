# data_logger.py: Handles logging results to a local CSV file.

import os
import datetime
import csv
import config


LOGGING_DISABLED = os.environ.get('DISABLE_LOGGING', 'False').lower() == 'true'

if LOGGING_DISABLED:
    print("Local CSV logging is DISABLED via environment variable.")

# Define the expected header for our log file
LOG_HEADER = [
    "Timestamp", "Session ID", "Question", "Answer", "Correctness Score",
    "Explanation Score", "Final Score", "Time Taken (s)", "Uncertainty",
    "Concept Gap", "Persona", "Evaluation", "Fallout Triggered"
]

def setup_local_csv_logging():
    """Checks if the local CSV log file exists and creates it with a header if not."""
    
    global LOGGING_DISABLED

    if LOGGING_DISABLED:
        return # Do nothing

    if not os.path.exists(config.LOCAL_LOG_FILE):
        try:
            with open(config.LOCAL_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(LOG_HEADER)
            print(f"Created local log file: {config.LOCAL_LOG_FILE}")
        except Exception as e:
            print(f"Error creating local log file (check permissions): {e}")
            print("--- Logging will be disabled for this session. ---")
            # Disable logging for this session if we can't create the file
            LOGGING_DISABLED = True


def log_to_csv(payload):
    """Appends a new row to the local CSV file."""
    # --- NEW: Check if logging is disabled ---
    if LOGGING_DISABLED:
        return # Do nothing

    try:
        with open(config.LOCAL_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(payload['row_data'])
    except Exception as e:
        print(f"Error writing to local CSV file: {e}")

def get_log_payload(session_id, question, answer, scores, signals, time_taken, evaluation, fallout=False):
    """Prepares the data row for logging."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    correctness = scores.get("correctness", "N/A")
    explanation = scores.get("explanation", "N/A")
    final = scores.get("final", "N/A")
    uncertainty = signals.get("uncertainty_detected", "N/A")
    concept_gap = signals.get("correctness_explanation_gap", "N/A")
    persona = signals.get("persona", "N/A")

    row_data = [
        timestamp, session_id, question, answer, correctness, explanation,
        final, time_taken, uncertainty, concept_gap, persona, evaluation, fallout
    ]
    return {"row_data": row_data}

