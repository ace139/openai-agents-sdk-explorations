import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from agents import Agent, function_tool

# Load environment variables from .env file in the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Database path
DB_NAME = "health_assistant.db"
DB_SUBDIRECTORY = "db"
DB_PATH = PROJECT_ROOT / DB_SUBDIRECTORY / DB_NAME


@function_tool
def verify_user_identity(user_id: int) -> str:
    """Verifies user identity by looking up the user_id in the users table of health_assistant.db.
    Returns a welcome message with the user's full name if found, or an error message if not found.
    Args:
        user_id: The integer ID of the user to verify.
    """
    if not DB_PATH.exists():
        return f"Database file not found at {DB_PATH.resolve()}. Please ensure it's initialized correctly (e.g., by running db/init_db.py)."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT first_name, last_name FROM users WHERE id = ?", (user_id,)
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            first_name, last_name = result
            return f"Verification successful. Welcome, {first_name} {last_name}!"
        else:
            return f"User ID {user_id} not found. Please provide a valid ID."
    except sqlite3.Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


# Define the agent
identity_verification_agent = Agent(
    name="IdentityVerifierAgent",
    instructions=(
        "You are an AI assistant responsible for verifying user identity. "
        "Your primary goal is to greet users after confirming their identity using their provided ID. "
        "Follow these steps:\n"
        "1. If the user hasn't provided an ID, politely ask them for their user ID. For example: 'Hello! To proceed, please provide your user ID.'\n"
        "2. Once the user provides an ID, use the 'verify_user_identity' tool to check it against the database.\n"
        "3. If the tool confirms the identity (e.g., 'Verification successful. Welcome, [Name]!'), respond with a friendly two-part message:\n"
        "   - Blank line\n"
        "   - First line: 'Verification successful! ✅'\n"
        "   - Blank line\n"
        "   - Second part: 'Hi [First Name], how are you doing today? I'm here to assist you with your health and wellbeing.'\n"
        "4. If the tool indicates the ID was not found (e.g., 'User ID [ID] not found...'), inform the user clearly and ask them to provide a correct ID. For example: 'It seems that ID is not in our records. Could you please double-check and provide a valid user ID?'\n"
        "5. If the tool returns any other error, inform the user that there was a problem verifying their ID and suggest they try again later."
        "Be warm, friendly, and professional in your communication."
    ),
    tools=[verify_user_identity],
    model="gpt-4.1-mini",
)
