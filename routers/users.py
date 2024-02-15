from typing import Annotated

from passlib.context import CryptContext
from pydantic import BaseModel,Field
from starlette import status

from models import Users
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['user']
)
bycrpt_context =CryptContext(schemes=['bcrypt'],deprecated='auto')

class UserPassword(BaseModel):
    password:str
    new_password:str=Field(min_length=6)

class UserBase(BaseModel):
    username:str
    email:str
    first_name:str
    last_name:str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

@router.get("/details",status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication Failed")
    return db.query(Users).filter(Users.id== user.get('id')).first()

@router.put("update_password",status_code=status.HTTP_204_NO_CONTENT)
async def update_pasword(user:user_dependency, db:db_dependency, new_pass:UserPassword):
    if user is None:
        raise HTTPException(status_code=401,detail="authentication Failed")
    user_model=db.query(Users).filter(Users.id == user.get('id')).first()
    if not bycrpt_context.verify(new_pass.password,user_model.hashed_password):
        raise HTTPException(status_code=401,detail="Error on password change")
    user_model.hashed_password=bycrpt_context.hash(new_pass.new_password)
    db.add(user_model)
    db.commit()
