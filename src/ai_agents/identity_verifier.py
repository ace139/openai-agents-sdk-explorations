import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, function_tool, RunContextWrapper, handoff
from .agent_context import UserInteractionContext
from .mood_recorder_agent import mood_recorder_agent

# Load environment variables from .env file in the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Database path
DB_NAME = "health_assistant.db"
DB_SUBDIRECTORY = "db"
DB_PATH = PROJECT_ROOT / DB_SUBDIRECTORY / DB_NAME


@function_tool
def verify_user_identity(
    wrapper: RunContextWrapper[UserInteractionContext], user_id: int
) -> str:
    """Verifies user identity by looking up the user_id in the users table of health_assistant.db.
    Sets user_id in context upon successful verification.
    Returns a welcome message with the user's full name if found, or an error message if not found.

    Args:
        wrapper: The agent's run context, used to store the user_id.
        user_id: The integer ID of the user to verify.
    """
    # Ensure the database directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not DB_PATH.exists():
        wrapper.context.user_id = None
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
            wrapper.context.user_id = user_id  # Set user_id in context
            # Construct the exact success message the agent's instructions expect.
            success_message = (
                f"Verification successful. Welcome, {first_name} {last_name}!"
            )
            return success_message
        else:
            wrapper.context.user_id = None  # Ensure context is clear if user not found
            return f"User ID {user_id} not found. Please provide a valid ID."
    except sqlite3.Error as e:
        wrapper.context.user_id = None  # Ensure context is clear on database error
        return f"Database error: {e}"
    except Exception as e:
        wrapper.context.user_id = None  # Ensure context is clear on unexpected error
        return f"An unexpected error occurred: {e}"


# Define the agent
identity_verification_agent = Agent[UserInteractionContext](  # Added context type
    name="IdentityVerifierAgent",
    instructions=(
        "You are an AI assistant responsible for verifying user identity. "
        "Your primary goal is to greet users after confirming their identity using their provided ID. "
        "Follow these steps:\n"
        "1. If the user hasn't provided an ID, politely ask them for their user ID. For example: 'Hello! To proceed, please provide your user ID.'\n"
        "2. Once the user provides an ID, use the 'verify_user_identity' tool to check it against the database.\n"
        "3. If the `verify_user_identity` tool returns a message starting with 'Verification successful. Welcome,', this indicates success. You should then:\n"
        "   a. Extract the user's full name from the tool's message.\n"
        "   b. Respond with a friendly two-part message:\n"
        "      - Blank line\n"
        "      - First line: 'Verification successful! ✅'\n"
        "      - Blank line\n"
        "      - Second part: 'Hi [First Name from tool message], how are you doing today? I'm here to assist you with your health and wellbeing.'\n"
        "   c. Immediately after, smoothly handoff to the MoodRecorderAgent. Use the `transfer_to_MoodRecorderAgent` tool. You can say something like: 'Now, let's check in on your mood.' Do not wait for further user input before this handoff.\n"
        "4. If the tool indicates the ID was not found (e.g., 'User ID [ID] not found...'), inform the user clearly and ask them to provide a correct ID. For example: 'It seems that ID is not in our records. Could you please double-check and provide a valid user ID?'\n"
        "5. If the tool returns any other error, inform the user that there was a problem verifying their ID and suggest they try again later."
        "Be warm, friendly, and professional in your communication."
    ),
    tools=[verify_user_identity],
    handoffs=[handoff(mood_recorder_agent)],
    model="gpt-4.1-mini",
)
