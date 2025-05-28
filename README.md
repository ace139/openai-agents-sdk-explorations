# OpenAI Agents SDK Explorations: Health & Wellness AI Assistant

This project explores the capabilities of the OpenAI Agents SDK by building a Health & Wellness AI assistant. The assistant interacts with users through a command-line interface (CLI) and helps them track their health metrics, mood, and receive personalized meal plans.

## Features Implemented

### 1. Core Infrastructure
- **CLI Application**: Built using `typer` for a user-friendly command-line experience.
- **OpenAI Agents SDK**: Leverages the SDK for creating and orchestrating multiple AI agents.
- **SQLite Database**: Uses `health_assistant.db` for persistent storage of user data, health metrics, and conversation logs.
- **SQLAlchemy ORM**: `db/models.py` defines the database schema using SQLAlchemy.
- **Database Initialization**: `db/init_db.py` script populates the database with sample data for testing and demonstration.
- **Environment Configuration**: Uses a `.env` file for managing sensitive information like API keys.

### 2. Agent Orchestration
- **Centralized Runner**: `main.py` manages the main chat loop, agent execution, and transitions.
- **Shared Context**: `src/ai_agents/agent_context.py` defines `UserInteractionContext`, a Pydantic model that allows data (like `user_id` and `exit_requested` flags) to be shared and persisted across different agent runs and handoffs.
- **Agent Handoffs**: Agents seamlessly transfer control to one another based on predefined triggers and logic, creating a conversational flow.

### 3. Implemented AI Agents

The application features a sequence of specialized AI agents, each with a distinct role:

#### a. `IdentityVerifierAgent`
- **File**: `src/ai_agents/identity_verifier.py`
- **Responsibility**: Verifies the user's identity by checking the provided `user_id` against the `users` table in the database.
- **Functionality**:
    - Prompts the user for their ID if not provided.
    - Uses the `verify_user_identity` tool to validate the ID.
    - Greets the user with their name upon successful verification.
- **Handoff**: Transitions to the `MoodRecorderAgent` after successful verification.

#### b. `MoodRecorderAgent`
- **File**: `src/ai_agents/mood_recorder_agent.py`
- **Responsibility**: Collects and records the user's current mood.
- **Functionality**:
    - Asks the user how they are feeling.
    - Uses the `record_mood` tool to save the mood into the `wellbeing_logs` table, linked to the `user_id` from the shared context.
- **Handoff**: Transitions to the `CGMReadingCollectorAgent` after successfully recording the mood.

#### c. `CGMReadingCollectorAgent`
- **File**: `src/ai_agents/cgm_reading_collector.py`
- **Responsibility**: Collects and records the user's Continuous Glucose Monitoring (CGM) readings.
- **Functionality**:
    - Asks the user for their current glucose reading (in mg/dL).
    - Uses the `record_glucose_reading` tool to save the reading into the `cgm_readings` table.
    - Provides immediate feedback:
        - Positive affirmation if the reading is within the normal range (70-140 mg/dL).
        - Information if the reading is below or above the normal range.
- **Handoff**: Transitions to the `MealPlannerAgent` if the glucose reading is outside the normal range.

#### d. `MealPlannerAgent`
- **File**: `src/ai_agents/meal_planner_agent.py`
- **Responsibility**: Generates personalized meal recommendations based on the user's health profile and glucose status.
- **Functionality**:
    - Triggered when a CGM reading is out of the normal range.
    - Uses three tools:
        - `get_user_health_profile`: Retrieves the user's dietary preferences and medical conditions from the `users` table.
        - `get_glucose_history`: Fetches the last CGM reading, and average CGM readings for the last 3 and 7 days from the `cgm_readings` table.
        - `generate_meal_plan`: Crafts a meal plan for the next 3 meals. The LLM agent is instructed to consider the glucose status (high, low, normal), dietary preferences, and medical conditions to provide specific and actionable meal suggestions.
    - After providing the meal plan, it sets an `exit_requested` flag in the shared context, signaling the `main.py` loop to terminate the application.

### 4. Design Patterns & Principles
- **Functional Programming**: Agents and their tools are designed with a functional approach where possible.
- **Single Responsibility Principle**: Each agent has a clearly defined, single responsibility, promoting modularity and maintainability.
- **Shared Context Management**: Effective use of `UserInteractionContext` and `RunContextWrapper` for managing state across agent interactions.
- **Tool-Based Functionality**: Agents leverage `function_tool` decorators to define specific actions they can perform, often involving database interactions or complex logic.
- **Clear Agent Instructions**: Each agent is configured with detailed instructions guiding its behavior, decision-making, and interaction style.

## How to Run

1.  **Set up Environment**:
    *   Ensure Python is installed.
    *   Create a virtual environment: `python -m venv venv`
    *   Activate it: `source venv/bin/activate` (on macOS/Linux) or `venv\Scripts\activate` (on Windows).
    *   Install dependencies (assuming `uv` is used, as per project conventions):
        ```bash
        uv pip install -r requirements.txt 
        ```
        (Note: If `requirements.txt` is not yet created, list dependencies like `openai-agents`, `typer[all]`, `python-dotenv`, `sqlalchemy`, `pydantic`.)
    *   Create a `.env` file in the project root and add your `OPENAI_API_KEY`:
        ```
        OPENAI_API_KEY='your_openai_api_key_here'
        ```

2.  **Initialize Database**:
    *   Run the database initialization script:
        ```bash
        python -m db.init_db
        ```
    This will create `health_assistant.db` in the `db` directory and populate it with sample data.

3.  **Start the Application**:
    *   Run the main application:
        ```bash
        python main.py start
        ```

4.  **Interact with the Assistant**:
    *   The assistant will first ask for your User ID. You can use any ID from 1 to 100 (as generated by `init_db.py`).
    *   Follow the prompts to log your mood and glucose readings.
    *   If your glucose reading is out of range, you will receive a meal plan.
    *   Type `quit` or `exit` at any user prompt to terminate the session.

## Project Structure

```
openai-agents-sdk-explorations/
├── .env                  # Environment variables (OPENAI_API_KEY)
├── db/
│   ├── __init__.py
│   ├── init_db.py        # Script to initialize the database
│   ├── models.py         # SQLAlchemy database models
│   └── health_assistant.db # SQLite database file (created by init_db.py)
├── src/
│   ├── ai_agents/
│   │   ├── __init__.py
│   │   ├── agent_context.py          # Shared context for agents
│   │   ├── cgm_reading_collector.py  # CGM reading collector agent
│   │   ├── identity_verifier.py      # Identity verification agent
│   │   ├── meal_planner_agent.py     # Meal planning agent
│   │   └── mood_recorder_agent.py    # Mood recording agent
│   └── __init__.py
├── main.py               # Main CLI application entry point
├── README.md             # This file
└── ...                   # Other project files (e.g., requirements.txt)
```

This project serves as a practical example of building multi-agent systems with the OpenAI Agents SDK, demonstrating how to manage state, orchestrate agent handoffs, and integrate with external data sources like a database.
