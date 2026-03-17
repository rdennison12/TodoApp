from typing import Annotated
import os

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from models import Users
from database import SessionLocal
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix='/user',
    tags=['user']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)


def get_password_hash(password: str):
    return password_context.hash(password)

def get_user_id_key():
    """Returns the appropriate user id key based on environment"""
    env = os.getenv('ENV', 'production')
    return 'id' if env == 'test' else 'user_id'


# get_user and return all information about the currently logged-in user
@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_id_key = get_user_id_key()
    return db.query(Users).filter(Users.id == user.get(user_id_key)).first()


# endpoint to allow user to change their password
@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_id_key = get_user_id_key()
    user_model = db.query(Users).filter(Users.id == user.get(user_id_key)).first()
    if not password_context.verify(user_verification.current_password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Error on password change")
    user_model.hashed_password = get_password_hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


# endpoint to allow user to update their phone number
@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_id_key = get_user_id_key()
    user_model = db.query(Users).filter(Users.id == user.get(user_id_key)).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()
