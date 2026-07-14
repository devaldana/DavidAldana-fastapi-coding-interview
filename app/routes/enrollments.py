from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.user import User
from app.schemas.enrollments import EnrollmentCreate, EnrollmentRead

MAX_COURSES_PER_USER = 5
MAX_USERS_PER_COURSE = 20

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("/", response_model=list[EnrollmentRead])
def get_all(
    db: Session = Depends(get_db),
) -> list[EnrollmentRead]:
    return db.query(Enrollment).all()


@router.post("/", response_model=EnrollmentRead)
def create(
    payload: EnrollmentCreate,
    db: Session = Depends(get_db),
) -> EnrollmentRead:
    user = db.query(User).get(payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    course = db.query(Course).get(payload.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    already_enrolled = (
        db.query(Enrollment)
        .filter_by(user_id=payload.user_id, course_id=payload.course_id)
        .first()
    )
    if already_enrolled:
        raise HTTPException(
            status_code=409, detail="User is already enrolled in this course"
        )

    user_course_count = (
        db.query(Enrollment).filter_by(user_id=payload.user_id).count()
    )
    if user_course_count >= MAX_COURSES_PER_USER:
        raise HTTPException(
            status_code=409,
            detail=f"User cannot be enrolled in more than {MAX_COURSES_PER_USER} courses",
        )

    course_user_count = (
        db.query(Enrollment).filter_by(course_id=payload.course_id).count()
    )
    if course_user_count >= MAX_USERS_PER_COURSE:
        raise HTTPException(
            status_code=409,
            detail=f"Course cannot have more than {MAX_USERS_PER_COURSE} users",
        )

    enrollment = Enrollment(
        user_id=payload.user_id,
        course_id=payload.course_id,
    )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return enrollment


@router.get("/users/{user_id}/courses", response_model=list[EnrollmentRead])
def get_courses_for_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> list[EnrollmentRead]:
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(Enrollment).filter_by(user_id=user_id).all()


@router.get("/courses/{course_id}/users", response_model=list[EnrollmentRead])
def get_users_for_course(
    course_id: int,
    db: Session = Depends(get_db),
) -> list[EnrollmentRead]:
    course = db.query(Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return db.query(Enrollment).filter_by(course_id=course_id).all()


@router.delete("/")
def delete(
    payload: EnrollmentCreate,
    db: Session = Depends(get_db),
) -> dict:
    enrollment = (
        db.query(Enrollment)
        .filter_by(user_id=payload.user_id, course_id=payload.course_id)
        .first()
    )

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    db.delete(enrollment)
    db.commit()

    return {"detail": "Enrollment deleted"}
