from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CourseBase(BaseModel):
    title: str
    description: str
    difficulty: str
    duration: str
    image_url: Optional[str] = None

class CourseSchema(CourseBase):
    id: int

    class Config:
        orm_mode = True

class CourseRecommendationSchema(CourseSchema):
    ai_reason: str


class UserProgressSchema(BaseModel):
    course_id: int
    progress_percentage: int
    course: CourseSchema

    class Config:
        orm_mode = True

class UserDashboardSchema(BaseModel):
    id: int
    username: str
    total_learning_hours: float
    modules_mastered: int
    progress_streak_days: int
    progresses: List[UserProgressSchema] = []

    class Config:
        orm_mode = True

class CuratedArticleSchema(BaseModel):
    id: int
    title: str
    source: str
    url: str
    expert_insight: str

    class Config:
        orm_mode = True
