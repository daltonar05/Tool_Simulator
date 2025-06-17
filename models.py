from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# In models.py - Add these imports at the top
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey  # <-- Add ForeignKey
from sqlalchemy.orm import relationship  # <-- Ensure this is imported

class User(Base):
    __tablename__ = 'users'  # Ensure table name matches ForeignKey reference
    id = Column(Integer, primary_key=True)
    username = Column(String)
    hashed_password = Column(String)
    is_approved = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Add relationship
    simulations = relationship("Simulation", back_populates="user")

class Simulation(Base):
    __tablename__ = 'simulations'
    id = Column(Integer, primary_key=True)
    planner_name = Column(String)
    filename = Column(String)
    
    # Corrected ForeignKey with proper imports
    user_id = Column(Integer, ForeignKey('users.id'))  # Now using imported ForeignKey
    
    # Relationship with back_populates
    user = relationship("User", back_populates="simulations")
