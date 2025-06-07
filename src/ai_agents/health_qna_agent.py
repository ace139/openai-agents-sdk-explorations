import sqlite3
from pathlib import Path
from typing import Annotated
from pydantic import Field
from agents import Agent, function_tool, RunContextWrapper
from .agent_context import UserInteractionContext

# Database path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_NAME = "health_assistant.db"
DB_SUBDIRECTORY = "db"
DB_PATH = PROJECT_ROOT / DB_SUBDIRECTORY / DB_NAME


@function_tool
def get_user_health_profile(
    wrapper: RunContextWrapper[UserInteractionContext]
) -> str:
    """Retrieves the user's health profile including dietary preferences and medical conditions
    to provide personalized answers.
    
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
def get_health_information(
    wrapper: RunContextWrapper[UserInteractionContext],
    query: Annotated[
        str,
        Field(
            description="The health topic or question from the user"
        ),
    ]
) -> str:
    """Provides information about health topics based on the user's query.
    
    Args:
        wrapper: The agent's run context, containing the user_id.
        query: The health topic or question from the user.
        
    Returns:
        Information about the requested health topic.
    """
    # Health information database - in a real system, this would be more sophisticated,
    # perhaps using a vector database or external API. For now, we'll use a simple 
    # dictionary for demonstration purposes.
    
    health_topics = {
        "diabetes": """
            Diabetes is a chronic health condition that affects how your body turns food into energy. 
            Most of the food you eat is broken down into sugar (glucose) and released into your bloodstream. 
            When your blood sugar goes up, it signals your pancreas to release insulin, which helps your 
            body's cells use the blood sugar for energy.
            
            There are several types of diabetes:
            - Type 1: The body doesn't make insulin. This is thought to be caused by an autoimmune reaction.
            - Type 2: The body doesn't use insulin well and can't keep blood sugar at normal levels.
            - Gestational: Develops in pregnant women who have never had diabetes.
            
            Managing diabetes involves monitoring blood sugar levels, taking medications as prescribed, 
            eating healthy foods, and staying physically active.
        """,
        
        "glucose": """
            Glucose is a simple sugar and an important carbohydrate in biology. It's one of the primary 
            molecules which serve as energy sources for plants and animals. Glucose is a monosaccharide 
            containing six carbon atoms and an aldehyde group, and is therefore an aldohexose.
            
            Normal blood glucose (blood sugar) levels are:
            - Fasting: 70-100 mg/dL
            - Before meals: 70-130 mg/dL
            - After meals (1-2 hours): Less than 180 mg/dL
            
            Consistently high blood glucose levels can indicate diabetes or prediabetes, 
            while consistently low levels might indicate other health issues.
        """,
        
        "hypertension": """
            Hypertension, or high blood pressure, is a common condition where the long-term force of 
            the blood against your artery walls is high enough that it may eventually cause health problems, 
            such as heart disease.
            
            Blood pressure is determined by the amount of blood your heart pumps and the amount of 
            resistance to blood flow in your arteries. The more blood your heart pumps and the narrower 
            your arteries, the higher your blood pressure.
            
            Normal blood pressure is less than 120/80 mm Hg. Hypertension is defined as a pressure of 
            130/80 mm Hg or higher. Lifestyle changes and medications can help control hypertension.
        """,
        
        "diet": """
            A healthy diet is essential for good health and nutrition. It protects against many chronic 
            diseases, such as heart disease, diabetes, and cancer. It can also help maintain a healthy 
            body weight.
            
            A healthy diet includes:
            - Fruits, vegetables, legumes (e.g., lentils and beans)
            - Nuts and whole grains (e.g., unprocessed maize, millet, oats, wheat, and brown rice)
            - At least 400 g (5 portions) of fruits and vegetables per day
            - Less than 10% of total energy intake from free sugars
            - Less than 30% of total energy intake from fats
            - Less than 5 g of salt per day
            
            Individual dietary needs may vary based on age, gender, lifestyle, degree of physical activity, 
            and medical conditions.
        """,
        
        "exercise": """
            Regular physical activity is one of the most important things you can do for your health. 
            Being physically active can improve your brain health, help manage weight, reduce the risk 
            of disease, strengthen bones and muscles, and improve your ability to do everyday activities.
            
            Adults should aim for:
            - At least 150 minutes a week of moderate-intensity activity or 75 minutes of vigorous activity
            - Muscle-strengthening activities on 2 or more days a week
            
            Even small amounts of physical activity are beneficial, and some physical activity is better 
            than none. Start with small amounts and gradually increase duration, frequency, and intensity.
        """,
    }
    
    # Try to find relevant information
    for topic, info in health_topics.items():
        if topic in query.lower():
            return info.strip()
            
    # For queries not matching specific topics, return a general response
    try:
        # Get user's medical conditions for context
        profile_info = get_user_health_profile(wrapper)
        
        return (
            f"I don't have specific information about '{query}' in my knowledge base. "
            f"Here's what I know about you based on your profile:\n\n{profile_info}\n\n"
            f"For specific health questions about {query}, I recommend consulting with "
            f"your healthcare provider who knows your medical history and can provide "
            f"personalized advice."
        )
    except Exception:
        return (
            f"I don't have specific information about '{query}' in my knowledge base. "
            f"For specific health questions, I recommend consulting with a healthcare "
            f"provider who can provide personalized advice based on your medical history."
        )


# Define the Health QnA agent
health_qna_agent = Agent[UserInteractionContext](
    name="HealthQnAAgent",
    instructions="""You are a health Q&A assistant that provides accurate, helpful information about health topics.
    
When asked a health question:
1. First, use get_health_information to retrieve information about the topic
2. If applicable, use get_user_health_profile to consider the user's health profile for more personalized responses
3. Keep responses clear, concise, and informative
4. Be honest when you don't know something
5. Don't diagnose specific conditions or provide medical advice
6. Always remind users to consult healthcare professionals for personal medical advice

Important guidelines:
- Provide evidence-based information when available
- Focus on answering the specific question asked
- After answering the health question, gently encourage the user to continue with their previous activity
- Be supportive and empathetic while maintaining professionalism

Example response structure:
1. Brief acknowledgment of the question
2. Factual answer based on available information
3. Personalization based on user profile when relevant
4. Brief reminder about consulting healthcare providers if needed
5. Gentle transition back to the original conversation flow""",
    tools=[get_user_health_profile, get_health_information],
    model="gpt-4.1-mini",
)
