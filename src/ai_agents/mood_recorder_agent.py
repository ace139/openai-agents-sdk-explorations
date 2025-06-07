import sqlite3
from pathlib import Path
from typing import Annotated
from pydantic import Field
from agents import Agent, function_tool, RunContextWrapper, handoff
from .agent_context import UserInteractionContext
from .cgm_reading_collector import cgm_reading_collector_agent
from .health_qna_agent import health_qna_agent

# Database path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_NAME = "health_assistant.db"
DB_SUBDIRECTORY = "db"
DB_PATH = PROJECT_ROOT / DB_SUBDIRECTORY / DB_NAME


@function_tool
def record_user_mood(
    wrapper: RunContextWrapper[UserInteractionContext],
    mood: Annotated[
        str,
        Field(
            description="The user's stated mood. Examples: happy, sad, energized, lazy, tired"
        ),
    ],
) -> str:
    """Records the user's mood into the wellbeing_logs table in the database.

    Args:
        wrapper: The agent's run context, containing the user_id.
        mood: The mood described by the user.
    """
    if wrapper is None or wrapper.context is None:
        return "Error: System error. Please try again."

    user_id = wrapper.context.user_id
    
    if user_id is None:
        return "Error: User ID is not available. Please verify your identity first."

    if not DB_PATH.exists():
        return f"Error: Database file not found at {DB_PATH.resolve()}. Cannot record mood."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO wellbeing_logs (user_id, mood) VALUES (?, ?)",
            (user_id, mood),
        )
        conn.commit()
        conn.close()
        return f"Your mood has been recorded as '{mood}' for user ID {user_id}."
    except sqlite3.Error as e:
        return f"Database error while recording mood: {e}"
    except Exception as e:
        return f"An unexpected error occurred while recording mood: {e}"


@function_tool
def record_mood(
    wrapper: RunContextWrapper[UserInteractionContext],
    mood: Annotated[
        str,
        Field(
            description="The user's mood, extracted from their response (e.g., 'happy', 'tired', 'lazy')"
        ),
    ],
) -> str:
    """Records the extracted mood in the database.

    Args:
        wrapper: The agent's run context, containing the user_id.
        mood: The mood to record, already extracted from user input.
    """
    if wrapper is None or wrapper.context is None:
        return "Error: System error. Please try again."

    user_id = wrapper.context.user_id
    
    if user_id is None:
        return "Error: User ID is not available. Please verify your identity first."

    if not DB_PATH.exists():
        return f"Error: Database file not found at {DB_PATH.resolve()}. Cannot record mood."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO wellbeing_logs (user_id, mood) VALUES (?, ?)",
            (user_id, mood),
        )
        conn.commit()
        conn.close()
        return f"Successfully recorded your mood as '{mood}'. Is there anything else you'd like to share about how you're feeling?"
    except sqlite3.Error:
        return "Error: Could not record your mood. Please try again."
    except Exception:
        return "Error: An unexpected error occurred. Please try again later."


mood_recorder_agent = Agent[UserInteractionContext](
    name="MoodRecorderAgent",
    instructions="""You are an AI assistant that helps users log their mood. Users have already been verified, and their user_id is available in your context.

Follow these steps:

1. First, ask the user about their mood with a friendly question like "How are you feeling today?"

2. When the user responds, extract their mood from their response. Pay attention to emotional keywords and phrases like:
   - Basic emotions: happy, sad, angry, tired, energetic, stressed, calm, etc.
   - Phrases that imply emotions: "feeling down", "bit lazy", "low energy", etc.
   - Context clues that suggest a mood

3. IMMEDIATELY use the record_mood tool to record the extracted mood. Pass ONLY the mood keyword or short phrase.
   - GOOD examples: "tired", "happy", "bit lazy", "stressed out"
   - BAD examples: passing the user's entire response or long descriptions

4. Share the confirmation message with the user.

5. After successfully recording the user's mood, smoothly transition to the CGM reading collector by saying something like: "Now, let's check your glucose levels. What is your current glucose reading in mg/dL?" Then hand off to the CGMReadingCollectorAgent using the transfer_to_CGMReadingCollectorAgent tool. Do not wait for further user input before this handoff.

6. If the user asks a health-related question instead of responding with their mood, use the answer_health_question tool to address their question. After answering, gently remind them that you're trying to record their mood and ask again how they're feeling today.

IMPORTANT: Do NOT ask for user ID. The user_id is already in your context. Your job is to extract the mood from the user's response and record it using the record_mood tool.""",
    tools=[
        record_mood,
        health_qna_agent.as_tool(
            tool_name="answer_health_question",
            tool_description="Answers health-related questions from the user"
        )
    ],
    handoffs=[handoff(cgm_reading_collector_agent)],
    model="gpt-4.1-mini",  # Or your preferred model
)
