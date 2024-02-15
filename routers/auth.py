from datetime import timedelta, datetime

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from redis import Redis
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import redis
import json
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '2db1ee71160723e417549609128a45a3128c4fbde38da3efe6a3e43e3aa61c7c'
ALGORITHM = 'HS256'

bycrpt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
ouath2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

redis_client = redis.Redis(host='localhost', port=6379, db=0)
class UserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
async def get_redis_client() -> Redis:
    """
    Dependency function to get a Redis client.
    Replace the parameters according to your Redis connection configuration.
    """
    redis_client = Redis(host="localhost", port=6379, db=0)
    try:
        yield redis_client
    finally:
        redis_client.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bycrpt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta, deltatime=None):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(ouath2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: int = payload.get('role')


        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, new_user: UserRequest):
    new_user_model = Users(
        email=new_user.email,
        username=new_user.username,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        role=new_user.role,
        hashed_password=bycrpt_context.hash(new_user.password),
        is_active=True

    )
    redis_data = json.dumps({"username": new_user_model.username, "email": new_user_model.email,  "first_name":new_user_model.first_name,"last_name":new_user_model.last_name,"role":new_user_model.role})
    redis_client.set(new_user_model.username,redis_data)
    db.add(new_user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency,redis_client: Redis = Depends(get_redis_client)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate")
    user_data = redis_client.get(user.username)
    print(user_data)
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}


@router.get("/{user_name}")
async def get_user(user_name: str, redis_client: Redis = Depends(get_redis_client)):

    user_data = redis_client.get(user_name)
    if not user_data:

        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_data