from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    total_learning_hours = Column(Float, default=0.0)
    modules_mastered = Column(Integer, default=0)
    progress_streak_days = Column(Integer, default=0)

    progresses = relationship("UserProgress", back_populates="user")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    difficulty = Column(String) # Beginner, Intermediate, Advanced
    duration = Column(String) # e.g. "4 Hours"
    image_url = Column(String, nullable=True)

    progresses = relationship("UserProgress", back_populates="course")

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    progress_percentage = Column(Integer, default=0)

    user = relationship("User", back_populates="progresses")
    course = relationship("Course", back_populates="progresses")

class CuratedArticle(Base):
    __tablename__ = "curated_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    source = Column(String) # e.g., Udemy, GeeksforGeeks
    url = Column(String)
    expert_insight = Column(String)
