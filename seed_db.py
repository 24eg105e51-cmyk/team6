from database import engine, SessionLocal
import models

def seed_courses():
    db = SessionLocal()
    if db.query(models.Course).count() == 0:
        print("Seeding courses...")
        courses = [
            models.Course(title='Intro to Python', description='Learn the basics of Python programming, data structures, and simple algorithms.', difficulty='Beginner', duration='4 Hours', image_url=''),
            models.Course(title='React for Beginners', description='Master component-based architecture and state mapping with Vite and React.', difficulty='Beginner', duration='6 Hours', image_url=''),
            models.Course(title='Advanced Tailwind CSS', description='Learn how to build stunning UI with complex grids, flexbox, and custom config plugins.', difficulty='Intermediate', duration='3 Hours', image_url=''),
            models.Course(title='FastAPI Microservices', description='Build scalable async architectures backed by SQLAlchemy and PostgreSQL.', difficulty='Intermediate', duration='8 Hours', image_url=''),
            models.Course(title='Framer Motion Animations', description='Bring your React apps to life with sophisticated, physics-based micro-interactions.', difficulty='Advanced', duration='5 Hours', image_url=''),
            models.Course(title='Machine Learning 101', description='A gentle introduction to predictive modeling and data wrangling.', difficulty='Beginner', duration='10 Hours', image_url=''),
        ]
        db.bulk_save_objects(courses)
        db.commit()
    db.close()

if __name__ == '__main__':
    models.Base.metadata.create_all(bind=engine)
    seed_courses()
    print("Seeding complete.")
