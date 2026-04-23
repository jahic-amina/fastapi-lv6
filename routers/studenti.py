import uuid

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import get_session
from models import Student, StudentCreate, StudentRead
from auth.config import current_verified_user
from auth.users import User, Role
from tasks.audit import (
    log_student_created,
    log_student_updated,
    log_student_deleted,
)

router = APIRouter(prefix="/studenti", tags=["studenti"])


def require_admin(user: User = Depends(current_verified_user)):
    if user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Samo admin može ovu akciju")
    return user


@router.get("/", response_model=list[StudentRead])
async def get_all(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Student))
    return result.scalars().all()


@router.get("/{student_id}", response_model=StudentRead)
async def get_one(student_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student nije pronađen")
    return student


@router.post("/", response_model=StudentRead, status_code=201)
async def create_student(
    student: StudentCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_verified_user),
):
    db_student = Student.from_orm(student)
    session.add(db_student)
    await session.commit()
    await session.refresh(db_student)
    background_tasks.add_task(log_student_created, str(db_student.id), user.email)
    return db_student


@router.put("/{student_id}", response_model=StudentRead)
async def update_student(
    student_id: uuid.UUID,
    student: StudentCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_admin),
):
    db = await session.get(Student, student_id)
    if not db:
        raise HTTPException(status_code=404, detail="Student nije pronađen")
    for k, v in student.dict().items():
        setattr(db, k, v)
    session.add(db)
    await session.commit()
    await session.refresh(db)
    background_tasks.add_task(log_student_updated, str(student_id), user.email, list(student.dict().keys()))
    return db


@router.delete("/{student_id}", status_code=204)
async def delete_student(
    student_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_admin),
):
    db = await session.get(Student, student_id)
    if not db:
        raise HTTPException(status_code=404, detail="Student nije pronađen")
    await session.delete(db)
    await session.commit()
    background_tasks.add_task(log_student_deleted, str(student_id), user.email)