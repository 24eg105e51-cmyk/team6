from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

def seed_db():
    db = SessionLocal()
    
    if db.query(models.User).filter_by(username="demo_user").first():
        print("Database already seeded!")
        return
        
    user = models.User(
        username="demo_user",
        total_learning_hours=64.5,
        modules_mastered=12,
        progress_streak_days=7
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    courses = [
        models.Course(title="Intro to Python", description="Learn Python basics.", difficulty="Beginner", duration="4 Hours"),
        models.Course(title="React for Beginners", description="Master component-based development.", difficulty="Beginner", duration="6 Hours"),
        models.Course(title="Advanced SQLAlchemy", description="Deep dive into Python ORMs.", difficulty="Intermediate", duration="5 Hours"),
        models.Course(title="Mastering Tailwind CSS", description="Build beautiful UIs fast.", difficulty="Intermediate", duration="3 Hours")
    ]
    db.add_all(courses)
    db.commit()
    
    for c in courses:
        db.refresh(c)
        prog = models.UserProgress(user_id=user.id, course_id=c.id, progress_percentage=100 if c.title == "Intro to Python" else 45)
        db.add(prog)
    db.commit()

    articles = [
        models.CuratedArticle(title="Understanding Glassmorphism in UI Design", source="GeeksforGeeks", url="https://www.geeksforgeeks.org", expert_insight="Utilize backdrop-blur to create depth in your UIs."),
        models.CuratedArticle(title="FastAPI Best Practices", source="Udemy Blog", url="https://www.udemy.com", expert_insight="Always validate your schemas using Pydantic."),
        models.CuratedArticle(title="CSS Gradients Techniques", source="GeeksforGeeks", url="https://www.geeksforgeeks.org", expert_insight="Layering multiple linear gradients can achieve stunning dynamic backgrounds.")
    ]
    db.add_all(articles)
    db.commit()
    
    db.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    models.Base.metadata.create_all(bind=engine)
    seed_db()
