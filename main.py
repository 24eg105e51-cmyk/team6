from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import random

from database import engine, Base, get_db
import models, schemas

# Auth setup
SECRET_KEY = "super-secret-key-for-skillpath-ai" # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days for prototyping

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user



app = FastAPI(title="SkillPath AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)

@app.post("/api/auth/register", response_model=schemas.UserDashboardSchema)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.UserDashboardSchema)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/api/courses/{course_id}/enroll", response_model=schemas.UserDashboardSchema)
def enroll_in_course(course_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    existing_progress = db.query(models.UserProgress).filter(
        models.UserProgress.user_id == current_user.id,
        models.UserProgress.course_id == course_id
    ).first()
    
    if existing_progress:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
        
    new_progress = models.UserProgress(
        user_id=current_user.id,
        course_id=course_id,
        progress_percentage=0
    )
    db.add(new_progress)
    db.commit()
    db.refresh(current_user)
    return current_user

@app.get("/api/recommendations", response_model=List[schemas.CourseRecommendationSchema])
def get_recommendations(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    enrolled_course_ids = [p.course_id for p in current_user.progresses] if current_user.progresses else []
    
    if enrolled_course_ids:
        unenrolled_courses = db.query(models.Course).filter(~models.Course.id.in_(enrolled_course_ids)).all()
    else:
        unenrolled_courses = db.query(models.Course).all()
        
    reasons = [
        "Based on your profile, this is a great starting point.",
        "This course aligns with your learning goals.",
        "Other learners highly recommended this.",
        "Perfect match for your skill level."
    ]
    
    recommendations = []
    for course in unenrolled_courses:
        recommendations.append(
            schemas.CourseRecommendationSchema(
                id=course.id,
                title=course.title,
                description=course.description,
                difficulty=course.difficulty,
                duration=course.duration,
                image_url=course.image_url,
                ai_reason=random.choice(reasons)
            )
        )
    return recommendations

@app.get("/api/dashboard/{user_id}", response_model=schemas.UserDashboardSchema)
def get_user_dashboard(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return {"id": user_id, "username": "Guest", "total_learning_hours": 0.0, "modules_mastered": 0, "progress_streak_days": 0, "progresses": []}
    return user

@app.get("/api/courses", response_model=List[schemas.CourseSchema])
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(models.Course).all()
    return courses

@app.get("/api/curated-articles", response_model=List[schemas.CuratedArticleSchema])
def get_curated_articles(db: Session = Depends(get_db)):
    articles = db.query(models.CuratedArticle).all()
    return articles
