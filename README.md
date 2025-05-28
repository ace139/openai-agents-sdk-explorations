# CLI Chat Application

A simple and interactive command-line chat application built with Python, Typer, and Rich. This application demonstrates a basic chat interface with color-coded messages and emoji support.

## Features

- 🎨 Color-coded messages for better readability
- 🤖 Agent responses in bold green
- 👤 User input prompts in bold blue
- 🚪 Graceful exit with "quit" or "exit" commands
- 🛡️ Error handling for unexpected inputs
- 🎭 Beautiful terminal formatting with Rich

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (Python package installer and resolver)
- SQLite3 (included with Python)

## Database Setup

This application uses SQLite for data storage. You'll need to manually initialize the database before running the application for the first time.

### Database Schema

The database includes the following tables:

- `users`: Stores user profile information
- `cgm_readings`: Stores Continuous Glucose Monitoring readings
- `wellbeing_logs`: Tracks user wellbeing metrics
- `conversation_logs`: Stores chat history   

### Initializing the Database

To manually initialize the database with synthetic data:

```bash
python db/init_db.py
```

This will:
1. Create a `db` directory if it doesn't exist
2. Create a SQLite database file at `db/health_assistant.db`
3. Generate synthetic data for 100 users
4. Create CGM readings and wellbeing logs for each user

## Synthetic Data Generation

The application includes a sophisticated synthetic data generation system that creates realistic health data for testing and development purposes.

### User Data

For each user, we generate:
- Realistic names and email addresses
- Randomly assigned cities
- Birth dates (ages 18-65)
- Dietary preferences (vegetarian, vegan, non-vegetarian)
- Medical conditions (Type 2 diabetes, hypertension, etc.)
- Physical limitations (mobility issues, visual impairment, etc.)

### CGM Readings

Continuous Glucose Monitoring readings are generated with realistic patterns based on the user's medical conditions. The generation includes:

1. **Condition-Specific Ranges**:
   - Normal: 70-140 mg/dL
   - Type 2 Diabetes: 90-250 mg/dL
   - Prediabetes: 80-200 mg/dL
   - Cardiovascular: 70-180 mg/dL
   - General: 60-140 mg/dL (for other conditions)

2. **Reading Types**:
   - Normal readings (70% probability)
   - Hyperglycemic readings (20% probability)
   - Hypoglycemic readings (10% probability)

3. **Temporal Patterns**:
   - 4 readings per day (breakfast, lunch, dinner, bedtime)
   - Random variations (±5%) to simulate real-world conditions
   - Natural fluctuations throughout the day

### Wellbeing Logs

Daily wellbeing logs include:
- Mood ratings (happy, sad, tired, energetic, etc.)
- Timestamped entries
- Random variations to simulate natural mood fluctuations

### Data Quality Features

- All timestamps are in UTC
- Data follows realistic patterns based on medical conditions
- Appropriate relationships between users and their data
- Sufficient variability to simulate real-world scenarios

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd openai-agents-sdk-explorations
   ```

2. Install the required dependencies using UV:
   ```bash
   uv pip install -r requirements.txt
   ```

   Or if you prefer to use UV's native dependency resolution:
   ```bash
   uv pip sync
   ```

## Usage

Start the chat application by running:

```bash
python main.py
```

### Commands

- Type your message and press Enter to chat with the agent
- Type `quit` or `exit` to end the chat session
- Use `Ctrl+C` to exit at any time

## Project Structure

```
.
├── .gitignore          # Git ignore file
├── README.md           # This file
├── main.py             # Main application entry point
├── pyproject.toml      # Project metadata and dependencies
├── uv.lock             # Lock file for reproducible dependencies
├── db/                 # Database related code
│   ├── __init__.py    # Database package
│   ├── models.py      # SQLAlchemy models
│   ├── database.py    # Database connection and session management
│   └── init_db.py     # Database initialization and data generation
└── src/                # Source code
    ├── ai_agents/     # AI agent implementations
    └── tools/         # Utility functions and tools
```

## Dependencies

### Core Dependencies

- [openai-agents](https://github.com/openai/openai-agents): Official OpenAI Agents SDK for building AI agents
- [SQLAlchemy](https://www.sqlalchemy.org/): Python SQL toolkit and ORM for database interactions
- [Typer](https://typer.tiangolo.com/): For building the CLI interface
- [Rich](https://github.com/Textualize/rich): For rich text and beautiful formatting in the terminal
- [Faker](https://faker.readthedocs.io/): For generating synthetic test data

### Development Dependencies

- [Ruff](https://beta.ruff.rs/): An extremely fast Python linter and code formatter

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

---

Happy chatting! 👋
