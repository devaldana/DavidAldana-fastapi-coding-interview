from fastapi import FastAPI

from app.routes import courses, enrollments, users

app = FastAPI(title="BEON High School API")

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
