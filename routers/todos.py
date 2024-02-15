from typing import Annotated

from pydantic import Field, BaseModel
from starlette import status

from models import Todos
from fastapi import APIRouter, Depends, HTTPException, Path, File,UploadFile
from sqlalchemy.orm import Session

from database import SessionLocal
from .auth import get_current_user


from fastapi.responses import FileResponse
import shutil
import os
router = APIRouter(
    tags=['User-Todo']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


class TodoSchema(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/todos/{todoId}", status_code=status.HTTP_200_OK)
async def read_by_id(user: user_dependency, db: db_dependency, todoId: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.id == todoId). \
        filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Item not Found.")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, new_todo: TodoSchema):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    newTodo = Todos(**new_todo.dict(), owner_id=user.get('id'))
    db.add(newTodo)
    db.commit()

    if newTodo is not None:
        return newTodo.title
    raise HTTPException(status_code=422, detail="data not pass")


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def todo_update(user: user_dependency, db: db_dependency, todo_request: TodoSchema, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id). \
        filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="todo not found.")
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id). \
        filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(Todos).filter(Todos.id == todo_id). \
        filter(Todos.owner_id == user.get('id')).delete()
    db.commit()

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):

    with open(f"/Users/divyanshsharma/Desktop/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename}


@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join("/Users/divyanshsharma/Desktop", filename)
    return FileResponse(file_path)






