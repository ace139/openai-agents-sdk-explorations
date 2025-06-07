# OpenAI Agents SDK Explorations: Health & Wellness AI Assistant

This project showcases the capabilities of the OpenAI Agents SDK by implementing a conversational Health & Wellness AI assistant. Users interact with the assistant via a command-line interface (CLI) to track health metrics, record mood, and receive personalized meal plans based on their data.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
  - [Core Infrastructure](#core-infrastructure)
  - [Agent Orchestration](#agent-orchestration)
  - [Implemented AI Agents](#implemented-ai-agents)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Running the Application](#running-the-application)
- [Key Architectural Concepts](#key-architectural-concepts)
- [Database Schema](#database-schema)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)

## Project Overview

The Health & Wellness AI Assistant is designed to simulate a multi-turn conversational experience where different specialized AI agents collaborate to assist the user. It demonstrates how to build modular, stateful agentic applications using the OpenAI Agents SDK, manage data persistence with SQLite, and structure a Python project for clarity and maintainability.

## Features

### Core Infrastructure

-   **CLI Application**: Interactive command-line interface built with `Typer` for a smooth user experience, featuring rich text formatting via the `Rich` library.
-   **OpenAI Agents SDK**: The backbone of the application, used for defining, running, and orchestrating AI agents.
-   **SQLite Database**: A local `health_assistant.db` file stores user profiles, health metrics (mood, CGM readings), and potentially conversation logs (though not explicitly implemented for logging in this version).
-   **SQLAlchemy ORM**: `db/models.py` defines the database schema using SQLAlchemy, providing an object-relational mapping for easier database interactions.
-   **Database Initialization**: The `db/init_db.py` script sets up the database schema and populates it with sample user data using `Faker` for testing and demonstration purposes.
-   **Environment Configuration**: Securely manages the OpenAI API key and model selection using a `.env` file, loaded via `python-dotenv`.
-   **Asynchronous Operations**: `main.py` utilizes `asyncio` for non-blocking I/O, particularly for handling user input and agent execution.

### Agent Orchestration

-   **Centralized Runner**: `main.py` acts as the primary orchestrator, managing the main chat loop, invoking agents using `Runner.run()`, and handling transitions between agents.
-   **Shared Context**: `src/ai_agents/agent_context.py` defines `UserInteractionContext`, a Pydantic model. This context is passed between agents, allowing them to share state (e.g., `user_id`, `exit_requested` flag) across different turns and handoffs, ensuring a cohesive conversational flow.
-   **Agent Handoffs**: Agents can hand off control to other agents. This is managed by the `Runner` based on the `last_agent` in the `RunResult`. The `main.py` loop updates the `current_agent` based on this, enabling a sequence of specialized interactions.

### Implemented AI Agents

The application orchestrates several AI agents, each with a specific role:

1.  **`IdentityVerifierAgent`**
    *   **File**: `src/ai_agents/identity_verifier.py`
    *   **Responsibility**: Verifies the user's identity.
    *   **Tools**: `verify_user_identity` (checks `user_id` against the database).
    *   **Workflow**: Prompts for `user_id`, validates it, and greets the user by name. Populates `user_id` in the shared context.
    *   **Handoff**: To `MoodRecorderAgent` upon successful verification.

2.  **`MoodRecorderAgent`**
    *   **File**: `src/ai_agents/mood_recorder_agent.py`
    *   **Responsibility**: Collects and records the user's current mood.
    *   **Tools**: `record_mood` (saves mood to `wellbeing_logs` table).
    *   **Workflow**: Asks the user about their mood and records the response.
    *   **Handoff**: To `CGMReadingCollectorAgent` after recording mood.

3.  **`CGMReadingCollectorAgent`**
    *   **File**: `src/ai_agents/cgm_reading_collector.py`
    *   **Responsibility**: Collects and records Continuous Glucose Monitoring (CGM) readings.
    *   **Tools**: `record_glucose_reading` (saves reading to `cgm_readings` table).
    *   **Workflow**: Asks for the current glucose reading, records it, and provides immediate feedback based on whether the reading is normal, high, or low.
    *   **Handoff**: To `MealPlannerAgent` if the glucose reading is outside the normal range (70-140 mg/dL). Otherwise, the conversation might end or transition to another agent if further logic were added.

4.  **`MealPlannerAgent`**
    *   **File**: `src/ai_agents/meal_planner_agent.py`
    *   **Responsibility**: Generates personalized meal recommendations.
    *   **Tools**:
        *   `get_user_health_profile`: Retrieves dietary preferences and medical conditions.
        *   `get_glucose_history`: Fetches recent and historical glucose data.
        *   `generate_meal_plan`: Crafts a meal plan (currently a placeholder in the tool, with the LLM agent expected to fill in details based on its instructions).
        *   `answer_health_question` (tool derived from `HealthQnAAgent`): Allows the user to ask health-related questions during meal planning.
    *   **Workflow**: Triggered by out-of-range CGM. Gathers health profile and glucose history. Generates a meal plan considering glucose status, preferences, and conditions. Sets an `exit_requested` flag in the context to terminate the application after providing the plan.
    *   **Handoff**: Sets `exit_requested` flag, leading to application termination.

5.  **`HealthQnAAgent`** (Used as a tool)
    *   **File**: `src/ai_agents/health_qna_agent.py`
    *   **Responsibility**: Provides answers to general health-related questions.
    *   **Tools**:
        *   `get_user_health_profile`: To tailor answers if possible.
        *   `get_health_information`: Retrieves information from a predefined knowledge base (currently a simple dictionary).
    *   **Workflow**: When invoked as a tool by `MealPlannerAgent`, it answers a user's health query. It's designed to provide general information and remind users to consult healthcare professionals.

## Technology Stack

-   **Programming Language**: Python (>=3.13 as per `pyproject.toml`)
-   **AI SDK**: `openai-agents` (OpenAI Agents SDK)
-   **CLI Framework**: `Typer`
-   **Rich Output**: `Rich` (for enhanced terminal UIs)
-   **Database**: SQLite
-   **ORM**: `SQLAlchemy`
-   **Environment Management**: `python-dotenv`
-   **Data Validation**: `Pydantic` (used for `UserInteractionContext`)
-   **Package Management & Build**: `uv` (implied by user rules, `pyproject.toml` for metadata)
-   **Code Linting/Formatting**: `Ruff` (implied by user rules and `.ruff_cache`)
-   **Data Generation (for DB init)**: `Faker`

## Project Structure

```
openai-agents-sdk-explorations/
├── .env.example                # Example environment file
├── .env                        # Local environment variables (OPENAI_API_KEY, OPENAI_MODEL) - Gitignored
├── .git/                       # Git repository data
├── .gitignore                  # Specifies intentionally untracked files
├── .python-version             # Specifies Python version for pyenv (if used)
├── .ruff_cache/                # Cache for Ruff linter - Gitignored
├── .venv/                      # Python virtual environment - Gitignored
├── db/
│   ├── __init__.py
│   ├── init_db.py            # Script to initialize and populate the database
│   ├── models.py             # SQLAlchemy ORM models
│   └── health_assistant.db     # SQLite database file - Gitignored
├── src/
│   ├── ai_agents/
│   │   ├── __init__.py
│   │   ├── agent_context.py      # Defines UserInteractionContext for shared state
│   │   ├── cgm_reading_collector.py # CGM Reading Collector Agent
│   │   ├── health_qna_agent.py   # Health Q&A Agent
│   │   ├── identity_verifier.py  # Identity Verifier Agent
│   │   ├── meal_planner_agent.py # Meal Planner Agent
│   │   └── mood_recorder_agent.py# Mood Recorder Agent
│   └── __init__.py
├── main.py                     # Main CLI application entry point (using Typer and asyncio)
├── pyproject.toml              # Project metadata and dependencies for PEP 517/PEP 621 build systems
├── README.md                   # This file
└── uv.lock                     # Lock file for uv package manager
```

## Prerequisites

-   Python (version >=3.13, as specified in `pyproject.toml`). You can manage Python versions using `pyenv` or install it directly.
-   `uv` (Python package installer and resolver, an extremely fast alternative to `pip` and `pip-tools`). If not installed, refer to [uv installation guide](https://github.com/astral-sh/uv).
-   An OpenAI API key.

## Setup and Installation

1.  **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd openai-agents-sdk-explorations
    ```

2.  **Set up Python Environment**:
    *   It's highly recommended to use a virtual environment. If you have `pyenv` and `pyenv-virtualenv`:
        ```bash
        pyenv install $(cat .python-version) # Installs Python version if not present
        pyenv virtualenv $(cat .python-version) openai-agents-env
        pyenv local openai-agents-env
        ```
    *   Alternatively, create a standard venv:
        ```bash
        python -m venv .venv
        ```
    *   Activate the virtual environment:
        *   On macOS/Linux: `source .venv/bin/activate`
        *   On Windows: `.venv\Scripts\activate`

3.  **Install Dependencies using `uv`**:
    ```bash
    uv pip install -r requirements.txt  # If requirements.txt is maintained
    # OR, if installing directly from pyproject.toml (preferred with uv)
    uv pip install . # Installs dependencies listed in pyproject.toml
    # For development dependencies (like Ruff):
    uv pip install .[dev]
    ```
    *(Note: The project uses `pyproject.toml` for dependencies. `uv` can install directly from it. If a `requirements.txt` is preferred for some workflows, it would typically be generated from `pyproject.toml` or `uv.lock` using `uv pip freeze > requirements.txt` or `uv pip compile pyproject.toml -o requirements.txt`.)*

4.  **Configure Environment Variables**:
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and add your OpenAI API key and desired model:
        ```plaintext
        OPENAI_API_KEY="your_actual_openai_api_key_here"
        OPENAI_MODEL="gpt-4.1-mini" # Or any other compatible model
        ```
        **Important**: Ensure `OPENAI_MODEL` is set, as agents might use it. The default in `.env.example` is `gpt-4.1-mini`.

5.  **Initialize the Database**:
    *   Run the database initialization script from the project root directory:
        ```bash
        python -m db.init_db
        ```
    *   This will create a `health_assistant.db` file in the `db/` directory and populate it with sample user data.

## Running the Application

1.  **Ensure your virtual environment is activated** and you are in the project root directory.
2.  **Start the CLI application**:
    ```bash
    python main.py start
    ```
3.  **Interact with the Assistant**:
    *   The assistant will first greet you and ask for your User ID. Based on the `db/init_db.py` script, sample user IDs are integers (e.g., 1, 2, 3, ... up to the number of users created, typically 10 or 100).
    *   Follow the prompts to:
        *   Verify your identity.
        *   Log your current mood.
        *   Log your CGM (Continuous Glucose Monitoring) reading.
    *   If your glucose reading is determined to be outside the normal range, the `MealPlannerAgent` will be invoked to provide you with a meal plan.
    *   During meal planning, if you have a health-related question, the `MealPlannerAgent` can use the `HealthQnAAgent`'s capabilities to answer it.
    *   After the meal plan is provided (or if the conversation flow ends earlier due to normal readings), the application will inform you and exit.
4.  **Exiting the Application**:
    *   You can type `quit` or `exit` at any user input prompt to terminate the session manually.
    *   The application will also exit automatically after the `MealPlannerAgent` completes its task.

## Key Architectural Concepts

-   **OpenAI Agents SDK**: The core framework enabling the creation of autonomous agents that can use tools and interact in a stateful manner. Each agent (`IdentityVerifierAgent`, `MealPlannerAgent`, etc.) is an instance of `agents.Agent`.
-   **Agent Design Philosophy**:
    *   **Functional Approach**: Tools are often simple Python functions decorated with `@function_tool`.
    *   **Single Responsibility**: Each agent is designed to handle a specific part of the conversation or a particular task, promoting modularity.
-   **`UserInteractionContext` (Shared Context)**:
    *   A Pydantic model (`src/ai_agents/agent_context.py`) that holds shared data across agent runs and handoffs.
    *   Instances of this context are passed to `Runner.run()`, allowing agents to access and modify shared state like `user_id` and the `exit_requested` flag.
    *   This is crucial for maintaining conversation continuity and statefulness.
-   **Agent Handoffs**: The `main.py` chat loop inspects `result.last_agent` after each `Runner.run()` call. If `result.last_agent` is different from the `current_agent`, it indicates a handoff, and `current_agent` is updated accordingly. This allows for dynamic transitions in the conversational flow.
-   **Tools (`@function_tool` and `agent.as_tool()`)**:
    *   Agents are equipped with tools to perform actions. These are typically Python functions.
    *   `@function_tool` decorator makes a Python function available as a tool for an agent.
    *   `another_agent.as_tool(tool_name="...", tool_description="...")` allows one agent to be used as a tool by another agent, enabling complex, hierarchical agent interactions (e.g., `MealPlannerAgent` using `HealthQnAAgent`).
-   **Agent Instructions**: Each agent is initialized with a detailed instruction prompt that guides its behavior, its use of tools, and its conversational style. These instructions are critical for the LLM to understand its role and objectives.
-   **`Runner.run()`**: The primary method from the SDK used to execute an agent with a given input and context. It returns a `RunResult` object containing the agent's output, the last agent that ran, and other metadata.

## Database Schema

The database (`health_assistant.db`) is managed by SQLAlchemy ORM, with models defined in `db/models.py`. Key tables include:

-   **`users`**: Stores user information (ID, name, email, dietary preferences, medical conditions).
-   **`wellbeing_logs`**: Records user mood entries (linked to `user_id`, mood, timestamp).
-   **`cgm_readings`**: Stores Continuous Glucose Monitoring readings (linked to `user_id`, reading value, timestamp).

Refer to `db/models.py` for detailed column definitions and relationships.

## Troubleshooting

-   **`OPENAI_API_KEY` not set/invalid**: Ensure your `.env` file is correctly configured with a valid OpenAI API key and that it's being loaded. The application usually prints an error message if the key is missing or incorrect.
-   **Python Version Issues**: Make sure you are using Python >=3.13. Use `python --version` to check.
-   **Dependency Problems**: If you encounter import errors, ensure all dependencies are installed correctly using `uv pip install .` in your activated virtual environment.
-   **Database Issues**: If `db/init_db.py` fails or the application can't find the database, check file paths and permissions. Ensure `health_assistant.db` is created in the `db/` directory after running the init script.
-   **Asyncio Event Loop Errors**: The `main.py` includes error handling for `RuntimeError` if `asyncio.run()` is called from an existing event loop (e.g., in a Jupyter notebook). Run the CLI from a standard terminal.

## Future Enhancements

-   **More Sophisticated Health Q&A**: Integrate with a vector database or external medical APIs for the `HealthQnAAgent` instead of a static dictionary.
-   **Expanded Agent Capabilities**: Add agents for exercise tracking, water intake, sleep monitoring, etc.
-   **Persistent Conversation History**: Store and retrieve conversation history for more contextual interactions over multiple sessions.
-   **Web Interface**: Develop a web-based UI instead of a CLI for broader accessibility.
-   **Advanced Error Handling and Logging**: Implement more robust error handling and structured logging.
-   **User Authentication**: Implement a more secure user authentication mechanism instead of simple ID verification.
-   **Testing**: Add comprehensive unit and integration tests for agents and tools.
