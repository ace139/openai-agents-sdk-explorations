import sqlite3
from pathlib import Path
from typing import Annotated
from pydantic import Field
from agents import Agent, function_tool, RunContextWrapper, handoff
from .agent_context import UserInteractionContext
from .meal_planner_agent import meal_planner_agent

# Database path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_NAME = "health_assistant.db"
DB_SUBDIRECTORY = "db"
DB_PATH = PROJECT_ROOT / DB_SUBDIRECTORY / DB_NAME

# Define normal glucose range (mg/dL)
NORMAL_MIN_GLUCOSE = 70
NORMAL_MAX_GLUCOSE = 140


@function_tool
def record_glucose_reading(
    wrapper: RunContextWrapper[UserInteractionContext],
    glucose_level: Annotated[
        float,
        Field(
            description="The user's current glucose reading in mg/dL (e.g., 95.5, 120, 83)"
        ),
    ],
) -> str:
    """Records the user's glucose reading into the glucose_readings table in the database.
    Provides feedback based on whether the reading is within normal range.

    Args:
        wrapper: The agent's run context, containing the user_id.
        glucose_level: The glucose reading in mg/dL.
    """
    if wrapper is None or wrapper.context is None:
        return "Error: System error. Please try again."

    user_id = wrapper.context.user_id
    
    if user_id is None:
        return "Error: User ID is not available. Please verify your identity first."

    if not DB_PATH.exists():
        return f"Error: Database file not found at {DB_PATH.resolve()}. Cannot record glucose reading."

    try:
        # Check if glucose_readings table exists, if not create it
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='glucose_readings'"
        )
        table_exists = cursor.fetchone()
        
        if not table_exists:
            # Create the table if it doesn't exist
            cursor.execute(
                """
                CREATE TABLE glucose_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    glucose_level REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
                """
            )
        
        # Insert the glucose reading
        cursor.execute(
            "INSERT INTO glucose_readings (user_id, glucose_level) VALUES (?, ?)",
            (user_id, glucose_level),
        )
        conn.commit()
        conn.close()
        
        # Determine if the reading is within normal range and generate appropriate response
        if NORMAL_MIN_GLUCOSE <= glucose_level <= NORMAL_MAX_GLUCOSE:
            return f"Your glucose reading of {glucose_level} mg/dL has been recorded. Great job! Your glucose level is within the normal range."
        elif glucose_level < NORMAL_MIN_GLUCOSE:
            return f"Your glucose reading of {glucose_level} mg/dL has been recorded. Your glucose level is below the normal range. Consider having a snack or meal soon."
        else:  # glucose_level > NORMAL_MAX_GLUCOSE
            return f"Your glucose reading of {glucose_level} mg/dL has been recorded. Your glucose level is above the normal range. Please follow your healthcare provider's recommendations for high glucose levels."
            
    except sqlite3.Error as e:
        return f"Database error while recording glucose reading: {e}"
    except Exception as e:
        return f"An unexpected error occurred while recording glucose reading: {e}"


# Define the CGM reading collector agent
cgm_reading_collector_agent = Agent[UserInteractionContext](
    name="CGMReadingCollectorAgent",
    instructions="""You are an AI assistant that helps users log their glucose (blood sugar) readings. Users have already been verified, and their user_id is available in your context.

Follow these steps:

1. First, ask the user for their current glucose reading with a friendly question like "What is your current glucose reading in mg/dL?"

2. When the user responds, extract the glucose reading value from their response. Look for:
   - A numeric value (e.g., "120", "95.5")
   - Units (mg/dL is the default if not specified)
   - Context clues about their glucose reading

3. IMMEDIATELY use the record_glucose_reading tool to record the extracted glucose reading. Pass ONLY the numeric value.
   - GOOD examples: 120, 95.5, 83
   - BAD examples: passing text like "my glucose is 120" or including units

4. Share the confirmation message with the user, which will include:
   - Confirmation that the reading was recorded
   - Feedback on whether the reading is within normal range (70-140 mg/dL)
   - A positive affirmation if the reading is within normal range

5. Analyze the glucose reading:
   - If the reading is NOT within the normal range (70-140 mg/dL), politely inform the user that you'll help them with meal recommendations based on their glucose levels. Say something like: "I notice your glucose level is outside the normal range. Let me help you with some meal recommendations." Then use the transfer_to_MealPlannerAgent tool to hand off to the meal planner. Do not wait for further user input before this handoff.
   - If the reading IS within the normal range, simply acknowledge this with a positive message.

6. If the user doesn't provide a clear numeric value, politely ask them to specify their glucose reading as a number.

IMPORTANT: Do NOT ask for user ID. The user_id is already in your context. Your job is to extract the glucose reading from the user's response and record it using the record_glucose_reading tool.""",
    tools=[record_glucose_reading],
    handoffs=[handoff(meal_planner_agent)],
    model="gpt-4.1-mini",  # Using the same model as other agents
)
