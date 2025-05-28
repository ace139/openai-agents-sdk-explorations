"""Database models for the health assistant application."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User model representing a health app user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    city = Column(String, nullable=False)
    date_of_birth = Column(DateTime(timezone=True), nullable=False)
    dietary_preference = Column(
        String, nullable=False
    )  # e.g., "vegetarian", "vegan", "non-vegetarian"
    medical_conditions = Column(
        Text, nullable=False
    )  # Comma-separated list of conditions
    physical_limitations = Column(
        Text, nullable=False
    )  # Comma-separated list of limitations
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    cgm_readings = relationship("CGMReading", back_populates="user")
    wellbeing_logs = relationship("WellbeingLog", back_populates="user")
    conversation_logs = relationship("ConversationLog", back_populates="user")


class CGMReading(Base):
    """Continuous Glucose Monitoring reading model."""

    __tablename__ = "cgm_readings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reading = Column(Float, nullable=False)  # Glucose reading in mg/dL
    timestamp = Column(DateTime(timezone=True), index=True, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="cgm_readings")


class WellbeingLog(Base):
    """Wellbeing log entry model."""

    __tablename__ = "wellbeing_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood = Column(String)  # e.g., "happy", "sad", "tired", "energetic"
    timestamp = Column(DateTime(timezone=True), index=True, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="wellbeing_logs")


class ConversationLog(Base):
    """Conversation log model for chat history."""

    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(
        String, index=True, nullable=False
    )  # To group messages in a conversation
    role = Column(String, nullable=False)  # "user", "assistant", "system"
    message = Column(Text, nullable=False)  # The actual message content
    timestamp = Column(DateTime(timezone=True), index=True, server_default=func.now())
    metadata_ = Column(
        "metadata", Text, nullable=True
    )  # JSON string for additional data

    # Relationships
    user = relationship("User", back_populates="conversation_logs")
