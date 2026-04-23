import uuid
from typing import Optional
from sqlmodel import Field, SQLModel


class StudentBase(SQLModel):
    ime: str
    prezime: str
    godina: int
    indeks: str
    email: Optional[str] = None


class Student(StudentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class StudentCreate(StudentBase):
    pass


class StudentUpdate(SQLModel):
    ime: Optional[str] = None
    prezime: Optional[str] = None
    godina: Optional[int] = None
    indeks: Optional[str] = None
    email: Optional[str] = None


class StudentRead(StudentBase):
    id: uuid.UUID