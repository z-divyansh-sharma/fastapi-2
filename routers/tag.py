from http.client import HTTPException

from pydantic import BaseModel

from models import Users, Tag
from fastapi import APIRouter, Depends
from database import SessionLocal
from typing import Annotated, List
from sqlalchemy.orm import Session


class UserBase(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    role: str


class TagUsersResponse(BaseModel):
    users: List[UserBase]


router = APIRouter(
    prefix='/tag',
    tags=['Tags']
)

router.post("/tags/")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/")
def create_tag(name: str, db: db_dependency):
    db_tag = Tag(name=name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.get("/all_tags")
def get_all(db: db_dependency):
    tag = db.query(Tag).all()
    return tag


@router.post("/users/{user_id}/tags/{tag_id}/")
def assign_tag_to_user(user_id: int, tag_id: int, db: db_dependency):
    user = db.query(Users).filter(Users.id == user_id).first()
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not user or not tag:
        raise HTTPException(status_code=404, detail="User or Tag not found")
    user.tags.append(tag)
    db.commit()
    return {"message": "Tag assigned to user successfully"}


@router.get("/users/{user_name}/tags/")
def get_user_tags(user_name: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == user_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.tags


@router.get("/tags/{tag_name}/users/")
def get_users_by_tag(tag_name: str, db: db_dependency):
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    users = [{"email": user.email, "username": user.username,
              "first_name": user.first_name, "last_name": user.last_name,
              "role": user.role} for user in tag.users]
    return users
