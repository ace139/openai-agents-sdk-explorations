import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Annotated
from pydantic import Field
from agents import Agent, function_tool, RunContextWrapper
from .agent_context import UserInteractionContext
from .health_qna_agent import health_qna_agent

# Database path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_NAME = "health_assistant.db"
DB_SUBDIRECTORY = "db"
DB_PATH = PROJECT_ROOT / DB_SUBDIRECTORY / DB_NAME


@function_tool
def get_user_health_profile(
    wrapper: RunContextWrapper[UserInteractionContext]
) -> str:
    """Retrieves the user's health profile including dietary preferences and medical conditions.
    
    Args:
        wrapper: The agent's run context, containing the user_id.
    
    Returns:
        A string containing the user's dietary preferences and medical conditions.
    """
    if wrapper is None or wrapper.context is None:
        return "Error: System error. Please try again."

    user_id = wrapper.context.user_id
    
    if user_id is None:
        return "Error: User ID is not available. Please verify your identity first."

    if not DB_PATH.exists():
        return f"Error: Database file not found at {DB_PATH.resolve()}. Cannot retrieve user profile."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user information including dietary preferences and medical conditions
        cursor.execute(
            """
            SELECT first_name, last_name, dietary_preference, medical_conditions 
            FROM users 
            WHERE id = ?
            """, 
            (user_id,)
        )
        
        user_info = cursor.fetchone()
        conn.close()
        
        if not user_info:
            return f"Error: User with ID {user_id} not found."
            
        first_name, last_name, dietary_preference, medical_conditions = user_info
        
        return (
            f"User Profile for {first_name} {last_name}:\n"
            f"- Dietary Preference: {dietary_preference}\n"
            f"- Medical Conditions: {medical_conditions}"
        )
        
    except sqlite3.Error as e:
        return f"Database error while retrieving user profile: {e}"
    except Exception as e:
        return f"An unexpected error occurred while retrieving user profile: {e}"


@function_tool
def get_glucose_history(
    wrapper: RunContextWrapper[UserInteractionContext]
) -> str:
    """Retrieves the user's glucose reading history, including the last reading, 
    average for the last 3 days, and average for the last 7 days.
    
    Args:
        wrapper: The agent's run context, containing the user_id.
    
    Returns:
        A string containing the user's glucose reading statistics.
    """
    if wrapper is None or wrapper.context is None:
        return "Error: System error. Please try again."

    user_id = wrapper.context.user_id
    
    if user_id is None:
        return "Error: User ID is not available. Please verify your identity first."

    if not DB_PATH.exists():
        return f"Error: Database file not found at {DB_PATH.resolve()}. Cannot retrieve glucose history."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get the most recent glucose reading
        cursor.execute(
            """
            SELECT reading, timestamp
            FROM glucose_readings
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
            """, 
            (user_id,)
        )
        
        last_reading = cursor.fetchone()
        
        if not last_reading:
            return "No glucose readings found for this user."
            
        last_glucose, last_timestamp = last_reading
        
        # Calculate the date ranges for 3 and 7 days ago
        now = datetime.now()
        three_days_ago = now - timedelta(days=3)
        seven_days_ago = now - timedelta(days=7)
        
        # Get average for last 3 days
        cursor.execute(
            """
            SELECT AVG(reading)
            FROM glucose_readings
            WHERE user_id = ? AND timestamp >= ?
            """, 
            (user_id, three_days_ago.strftime('%Y-%m-%d %H:%M:%S'))
        )
        
        avg_3days = cursor.fetchone()[0]
        
        # Get average for last 7 days
        cursor.execute(
            """
            SELECT AVG(reading)
            FROM glucose_readings
            WHERE user_id = ? AND timestamp >= ?
            """, 
            (user_id, seven_days_ago.strftime('%Y-%m-%d %H:%M:%S'))
        )
        
        avg_7days = cursor.fetchone()[0]
        
        conn.close()
        
        # Format the output with relevant information
        return (
            f"Glucose Reading History:\n"
            f"- Last Reading: {last_glucose} mg/dL\n"
            f"- Average (Last 3 Days): {avg_3days:.1f} mg/dL\n"
            f"- Average (Last 7 Days): {avg_7days:.1f} mg/dL\n"
            f"- Normal Range: 70-140 mg/dL"
        )
        
    except sqlite3.Error as e:
        return f"Database error while retrieving glucose history: {e}"
    except Exception as e:
        return f"An unexpected error occurred while retrieving glucose history: {e}"


@function_tool
def generate_meal_plan(
    wrapper: RunContextWrapper[UserInteractionContext],
    glucose_status: Annotated[
        str,
        Field(
            description="The status of the user's glucose levels (e.g., 'high', 'low', 'normal')"
        ),
    ],
) -> str:
    """Generates a personalized meal plan based on the user's glucose levels, dietary preferences, and medical conditions.
    
    Args:
        wrapper: The agent's run context, containing the user_id.
        glucose_status: The current status of the user's glucose levels.
    
    Returns:
        A string containing meal recommendations for the next three meals.
    """
    if wrapper is None or wrapper.context is None:
        return "Error: System error. Please try again."

    user_id = wrapper.context.user_id
    
    if user_id is None:
        return "Error: User ID is not available. Please verify your identity first."

    if not DB_PATH.exists():
        return f"Error: Database file not found at {DB_PATH.resolve()}. Cannot generate meal plan."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user's dietary preference and medical conditions
        cursor.execute(
            "SELECT dietary_preference, medical_conditions FROM users WHERE id = ?", 
            (user_id,)
        )
        
        user_info = cursor.fetchone()
        conn.close()
        
        if not user_info:
            return f"Error: User with ID {user_id} not found."
            
        dietary_preference, medical_conditions = user_info
        
        # Add the exit flag to context to signal application termination
        wrapper.context.exit_requested = True
        
        # Generate a formatted meal plan
        return (
            f"Based on your glucose status ({glucose_status}), dietary preference ({dietary_preference}), "
            f"and medical conditions ({medical_conditions}), here's your personalized meal plan:\n\n"
            f"Meal Plan for the Next 3 Meals:\n\n"
            f"1. *Next Meal*: This is a placeholder for meal recommendation - will be replaced by the agent's response.\n\n"
            f"2. *Following Meal*: This is a placeholder for meal recommendation - will be replaced by the agent's response.\n\n"
            f"3. *Later Meal*: This is a placeholder for meal recommendation - will be replaced by the agent's response.\n\n"
            f"Thank you for using the Health Assistant! The application will now exit."
        )
        
    except sqlite3.Error as e:
        return f"Database error while generating meal plan: {e}"
    except Exception as e:
        return f"An unexpected error occurred while generating meal plan: {e}"


# Define the meal planner agent
meal_planner_agent = Agent[UserInteractionContext](
    name="MealPlannerAgent",
    instructions="""You are an AI assistant specializing in personalized meal planning based on glucose readings and health profiles.

Follow these steps:

1. First, use the get_user_health_profile tool to retrieve the user's dietary preferences and medical conditions.

2. Then, use the get_glucose_history tool to analyze the user's glucose readings, including:
   - Their most recent glucose reading
   - The average reading for the last 3 days
   - The average reading for the last 7 days

3. Based on this information, determine if the user's glucose level is:
   - HIGH (above 140 mg/dL)
   - LOW (below 70 mg/dL)
   - NORMAL (between 70-140 mg/dL)

4. Generate appropriate meal recommendations considering:
   - If glucose is HIGH: Focus on low-glycemic foods, complex carbs, protein, and fiber
   - If glucose is LOW: Include foods that will raise blood sugar safely (e.g., fruits, whole grains)
   - If glucose is NORMAL: Balanced meals that help maintain stable glucose levels
   - ALWAYS respect their dietary preferences (vegetarian, vegan, non-vegetarian, etc.)
   - ALWAYS consider their medical conditions (diabetes, hypertension, etc.)

5. Use the generate_meal_plan tool with the appropriate glucose status parameter ('high', 'low', or 'normal'). 
   In your message to the user, replace the placeholders with SPECIFIC meal recommendations including:
   - Food items (be specific, not general categories)
   - Portion sizes when appropriate
   - Brief explanation of why these foods are recommended for their condition

6. If the user asks a health-related question during the meal planning process, use the answer_health_question tool to address their question, and then continue with providing meal recommendations.

7. After providing the meal plan, inform the user that the program will now exit. 
   The generate_meal_plan tool automatically sets an exit flag that will terminate the CLI program.

IMPORTANT: Provide DETAILED, SPECIFIC meal recommendations, not general advice. For example, instead of saying "eat low-glycemic foods," recommend specific meals like "1 cup of steel-cut oatmeal with cinnamon and 1 tablespoon of almonds."

Remember: The user's health profile and glucose readings are already in the database. You do not need to ask them for this information.""",
    tools=[
        get_user_health_profile, 
        get_glucose_history, 
        generate_meal_plan,
        health_qna_agent.as_tool(
            tool_name="answer_health_question",
            tool_description="Answers health-related questions from the user"
        )
    ],
    model="gpt-4.1-mini",
)
