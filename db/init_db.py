"""Initialize the database with sample data."""

import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Third-party imports
from faker import Faker

# Local imports
try:
    # For when run as a module
    from .models import Base, User, CGMReading, WellbeingLog
    from .database import engine, SessionLocal
except ImportError:
    # For when run directly
    from models import Base, User, CGMReading, WellbeingLog
    from database import engine, SessionLocal

# Initialize Faker
fake = Faker()

def generate_sample_users(count: int = 100) -> list[User]:
    """Generate sample user data."""
    users = []
    dietary_prefs = ["vegetarian", "vegan", "non-vegetarian"]
    medical_conditions = [
        "Type 2 diabetes",
        "Hypertension",
        "High cholesterol",
        "Heart disease",
        "Asthma",
        "Arthritis",
        "None"
    ]
    physical_limitations = [
        "Mobility issues",
        "Visual impairment",
        "Hearing impairment",
        "Limited dexterity",
        "None"
    ]

    for i in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
        
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            city=fake.city(),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=65),
            dietary_preference=random.choice(dietary_prefs),
            medical_conditions=", ".join(random.sample(medical_conditions, random.randint(1, 2))),
            physical_limitations=random.choice(physical_limitations),
        )
        users.append(user)
    
    return users



def generate_wellbeing_logs(user_id: int, days: int = 30) -> list[WellbeingLog]:
    """Generate wellbeing logs for a user."""
    logs = []
    moods = ["happy", "sad", "tired", "energetic", "stressed", "calm", "anxious", "excited"]
    now = datetime.now(timezone.utc)
    
    for day in range(days):
        # 70% chance of a log on any given day
        if random.random() < 0.7:
            log = WellbeingLog(
                user_id=user_id,
                mood=random.choice(moods),
                timestamp=now - timedelta(days=day, hours=random.randint(8, 20))
            )
            logs.append(log)
    
    return logs

def get_glucose_ranges(medical_conditions: str) -> dict:
    """Determine glucose ranges based on medical conditions."""
    conditions = medical_conditions.lower().split(", ")
    
    if "type 2 diabetes" in conditions:
        # Type 2 Diabetes: Wider range with more variability
        return {
            "normal": (70, 180),  # 60% chance
            "hyperglycemic": (181, 300),  # 30% chance
            "hypoglycemic": (40, 69),  # 10% chance
            "weights": [0.6, 0.3, 0.1]
        }
    elif "prediabetes" in conditions:
        # Prediabetes: Mostly normal with occasional highs
        return {
            "normal": (70, 140),  # 80% chance
            "hyperglycemic": (141, 199),  # 15% chance
            "hypoglycemic": (60, 69),  # 5% chance
            "weights": [0.8, 0.15, 0.05]
        }
    elif any(cond in conditions for cond in ["hypertension", "high cholesterol", "heart disease"]):
        # Cardiovascular conditions: Slightly elevated
        return {
            "normal": (80, 150),  # 85% chance
            "hyperglycemic": (151, 220),  # 10% chance
            "hypoglycemic": (60, 79),  # 5% chance
            "weights": [0.85, 0.1, 0.05]
        }
    else:
        # Healthy individuals: Tight control
        return {
            "normal": (70, 120),  # 95% chance
            "hyperglycemic": (121, 140),  # 4% chance
            "hypoglycemic": (65, 69),  # 1% chance
            "weights": [0.95, 0.04, 0.01]
        }

def generate_cgm_readings(user_id: int, medical_conditions: str, days: int = 30) -> list[CGMReading]:
    """Generate realistic CGM readings based on user's medical conditions."""
    readings = []
    now = datetime.now(timezone.utc)
    
    # Get appropriate glucose ranges
    ranges = get_glucose_ranges(medical_conditions)
    
    for day in range(days):
        # More readings during the day, fewer at night
        reading_times = (
            [8, 12, 16, 20]  # 4 readings/day (breakfast, lunch, dinner, bedtime)
            if random.random() > 0.3
            else [8, 12, 20]  # 3 readings/day (occasionally)
        )
        
        for hour in reading_times:
            # Add some randomness to the reading time
            minute = random.randint(0, 59)
            
            # Choose reading type based on weights
            reading_type = random.choices(
                ["normal", "hyperglycemic", "hypoglycemic"],
                weights=ranges["weights"]
            )[0]
            
            # Get the appropriate range
            min_val, max_val = ranges[reading_type]
            
            # Add some natural variability
            reading = random.uniform(min_val, max_val)
            
            # Add some realistic noise (±5%)
            reading *= random.uniform(0.95, 1.05)
            
            # Create the reading
            readings.append(CGMReading(
                user_id=user_id,
                reading=round(reading, 1),
                timestamp=now - timedelta(
                    days=day,
                    hours=24 - hour,
                    minutes=minute
                )
            ))
    
    return readings

def init_db() -> None:
    """Initialize the database with sample data."""
    # Ensure the db directory exists
    db_dir = Path("db")
    db_dir.mkdir(exist_ok=True)
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Generate and add users
        print("Generating 100 users...")
        users = generate_sample_users(100)
        db.add_all(users)
        db.commit()
        
        # For each user, generate related data
        for i, user in enumerate(users, 1):
            print(f"Generating data for user {i}/100...")
            
            # Generate CGM readings based on medical conditions
            cgm_readings = generate_cgm_readings(user.id, user.medical_conditions)
            db.add_all(cgm_readings)
            
            # Generate wellbeing logs
            wellbeing_logs = generate_wellbeing_logs(user.id)
            db.add_all(wellbeing_logs)
            
            # Commit after each user to avoid large transactions
            db.commit()
        
        print("✅ Database initialization complete!")
        print(f"Database location: {Path().absolute()}/health_assistant.db")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error initializing database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
