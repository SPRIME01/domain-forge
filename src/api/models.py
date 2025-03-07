"""Database models for the API."""
from sqlalchemy import Column, Integer, String
from src.infrastructure.database import Base

class Entity(Base):
    """Entity database model."""
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True)
    name = Column(String)
