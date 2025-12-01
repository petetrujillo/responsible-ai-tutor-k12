# config.py: Loads settings from the user-editable settings.ini file.

import os
import configparser

# This is the secure way to handle API keys.
# You will set 'GEMINI_API_KEY' in your hosting provider's dashboard.
API_KEY = os.environ.get('GEMINI_API_KEY')


# Create a config parser object
config = configparser.ConfigParser()

# Path to the settings file
settings_file = os.path.join(os.path.dirname(__file__), 'settings.ini')

# Read the settings file
if not os.path.exists(settings_file):
    raise FileNotFoundError("Critical Error: settings.ini file not found. Please create it.")
config.read(settings_file)

# --- Load Settings ---

# [General] Section
# We check if the API_KEY was loaded from the environment.
# If not (e.g., local testing), we fall back to the one in settings.ini.
if not API_KEY:
    print("Warning: GEMINI_API_KEY not set in environment. Falling back to settings.ini.")
    API_KEY = config.get('General', 'api_key', fallback=None)
    if not API_KEY or API_KEY == 'YOUR_GEMINI_API_KEY_HERE only on local copy':
        print("CRITICAL ERROR: API Key is not set in settings.ini or environment.")
        # You could raise an error here to stop the app
        # raise ValueError("API Key not found. Set it in settings.ini or as GEMINI_API_KEY env var.")

KB_FILE_PATH = os.path.join(os.path.dirname(__file__), config.get('General', 'lesson_file', fallback='LessonAILiteracy.txt'))

# [Tutor Behavior] Section
REMEDIATION_THRESHOLD = config.getint('Tutor Behavior', 'passing_score', fallback=70)
MAX_ATTEMPTS = config.getint('Tutor Behavior', 'max_attempts', fallback=2)
MAX_TIME_ON_QUESTION = config.getint('Tutor Behavior', 'max_time_on_question', fallback=120)
GRADER_DIFFICULTY = config.get('Tutor Behavior', 'grader_difficulty', fallback='Normal')


# --- Local CSV Configuration ---
# This remains the same, but data_logger.py will control if it's used
LOCAL_LOG_FILE = os.path.join(os.path.dirname(__file__), 'tutor_log.csv')
