from typing import Annotated
from pydantic import Field, BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Path, APIRouter, Request
from starlette import status
from models import Todos
from database import SessionLocal
from .auth import get_current_user
from .users import get_user_id_key
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie("access_token")
    return redirect_response


### Pages ###
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        access_token = request.cookies.get("access_token")
        user = await get_current_user(access_token)

        if user is None:
            return redirect_to_login()

        user_id = user[get_user_id_key()]
        todos = db.query(Todos).filter(Todos.owner_id == user_id).all()

        context = {
            "request": request,
            "todos": todos,
            "user": user,
        }
        return templates.TemplateResponse("todo.html", context)
    except (HTTPException, KeyError, TypeError):
        return redirect_to_login()


@router.get("/add-todo-page")
async def render_add_todo_page(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return redirect_to_login()

    try:
        current_user = await get_current_user(access_token)
    except HTTPException:
        return redirect_to_login()

    context = {"request": request, "user": current_user}
    return templates.TemplateResponse("add-todo.html", context)


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        access_token = request.cookies.get("access_token")
        user = await get_current_user(access_token)

        if user is None:
            return redirect_to_login()

        user_id = user[get_user_id_key()]
        todo = db.query(Todos).filter(Todos.id == todo_id).first()

        context = {
            "request": request,
            "todo": todo,
            "user": user,
        }
        return templates.TemplateResponse("edit-todo.html", context)
    except (HTTPException, KeyError, TypeError):
        return redirect_to_login()


### Endpoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == user.get(get_user_id_key())).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get(get_user_id_key()))
        .first()
    )

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    await check_if_user_none(user)

    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get(get_user_id_key()))
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    await check_if_user_none(user)

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get(get_user_id_key()))
        .first()
    )

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


async def check_if_user_none(user: dict):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get(get_user_id_key()))
        .first()
    )

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.query(Todos).filter(Todos.id == todo_id).filter(
        Todos.owner_id == user.get(get_user_id_key())
    ).delete()
    db.commit()
