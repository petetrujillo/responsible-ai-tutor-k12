**Responsible AI Tutor for K-12**
A Governance-First, Multi-Agent Tutoring System for Secondary Education

The Instructional AI Tutor is a Python-based educational platform designed to bridge the gap between abstract AI ethics and concrete technical implementation. Unlike "black box" AI tools, this system is engineered with a "Governance-First" architecture, where safety, transparency, and policy compliance are foundational to the code itself.

Designed specifically for the developmental needs of secondary students (grades 6-12), the system uses Retrieval-Augmented Generation (RAG) to restrict AI responses to vetted, district-approved curriculum materials, effectively eliminating hallucinations and ensuring content safety.

**Key Features:**

**Governance & Safety**
- Restricted Content (RAG): The AI is "leashed" to a local Knowledge Base (e.g., LessonAILiteracy.txt), preventing it from inventing facts or accessing the open internet for answers.
- Privacy by Design: Built to align with FERPA/COPPA mandates, ensuring student data is handled with strict role-based constraints.
- Safety Alerts: Automatically detects and flags high-risk inputs (e.g., self-harm, bullying) for immediate human intervention

**Pedagogical Intelligence**
Dual-Axis Scoring: Moves beyond "pass/fail" by evaluating student responses on two distinct metrics: Correctness (factual accuracy) and Explanation Quality (depth of understanding).

**Adaptive Feedback Loop:**
- Remediation: Detects low scores and offers simplified explanations.
- Fallout Handling: Identifies when a student is stuck (max attempts or idle time) and proactively moves them forward to prevent frustration.
- Multi-Agent Personas: dynamically switches between a "Strict Grader," a "Helpful Tutor," and a "Subject Matter Expert" depending on the student's needs.

**Technical & Operational**
- Transparent Logging: All interactions, scores, and latency metrics are logged locally to .csv for transparent auditing.
- Configurable Difficulty: Administrators can toggle grader strictness (Easy, Normal, Strict) via a simple configuration file.
- Multi-Agent Personas: dynamically switches between a "Strict Grader," a "Helpful Tutor," and a "Subject Matter Expert" depending on the student's needs.

**Technical & Operational**
- Transparent Logging: All interactions, scores, and latency metrics are logged locally to .csv for transparent auditing.
- Configurable Difficulty: Administrators can toggle grader strictness (Easy, Normal, Strict) via a simple configuration file.

**System Architecture**
The application operates as a Multi-Agent System  powered by Flask and Google Gemini:
- Orchestrator (app.py): Manages the web server and session state.
- Content Manager (knowledge_base.py): Parses the vetted lesson plan.
- Evaluator Agent (evaluator.py): Uses the LLM to grade answers against the ground truth.
- Tutor Agent (tutor.py): Generates conversational remediation or hints.
- Logger (data_logger.py): records session data for analytics.

**Getting Started**
Prerequisites
- Python 3.8+
- A Google Gemini API Key

**Installation**

**1 Clone the repository**

*Bash**
git clone https://github.com/yourusername/responsible-ai-tutor-k12.git
cd responsible-ai-tutor-k12

**2 Install dependencies**

**Bash**
pip install -r requirements.txt

**3 Configure the Application**
Rename settings.ini.example to settings.ini.
Open settings.ini and add your API key:

**Ini, TOML**
[General]
api_key = YOUR_GEMINI_API_KEY_HERE
lesson_file = LessonAILiteracy.txt

**4 Run the Application**
**Bash**
python app.py
Open your browser and navigate to http://localhost:5001.
