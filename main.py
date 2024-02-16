import time

from fastapi import FastAPI,Request
from starlette.responses import JSONResponse

from routers import users, admin
from routers import tag, auth, todos
from models import Base
from database import engine

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(tag.router)
