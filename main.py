from fastapi import FastAPI, HTTPException,Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
# ------------------------
# MySQL Connection
# ------------------------

DATABASE_URL = "mysql+pymysql://root:Mohan%40123@localhost:3306/college"

engine = create_engine(DATABASE_URL)
  
Sessionmysql = sessionmaker(bind=engine)

db = Sessionmysql()

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100))
    password = Column(String(100))

Base.metadata.create_all(bind=engine)





   




    

class Signup(BaseModel):
    name: str
    email: str
    password: str

# FastAPI

app = FastAPI()

# Create User
# ------------------------

@app.post("/signup")
def signup(user: Signup):

    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "User Created"
    }

# get api

@app.get("/users")
def get_users():

    users = db.query(User).all()

    db.close()

    return users


@app.get("/users/{email}")
def get_user(email: str):

    

    db_user = db.query(User).filter(User.email == email).first()

    if db_user is None:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.close()

    return db_user

# login api

class Login(BaseModel):
    email : str
    password : str

@app.post("/login")
def login(user: Login):
    db_user = db.query(User).filter(User.email == user.email).first()

    if db_user is None:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    if db_user.password != user.password:
        db.close()
        raise HTTPException(
            status_code =401,
            detail = "passwod invalid"
        )
    
   


# create put api

class UpdateUser(BaseModel):
    name : str
    email : str

# create endpoint

@app.put("/users/{old_email}")

def update_user(old_email: str, user: UpdateUser):

     exist_data = db.query(User).filter(User.email == old_email).first()

     
     if exist_data is None:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
     exist_data.name = user.name
     exist_data.email = user.email

     db.commit()

     db.refresh(exist_data)

     db.close()

     return {
        "message": "User updated successfully",
        "data": exist_data
    }

# create delete api

@app.delete("/users/{id}")
def delete_user(id: int):
    user_data = db.query(User).filter(User.id == id).first()

    if user_data is None:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    db.delete(user_data)

    db.commit()

    db.close()

    return {
        "message": "delete user successfully"
    }

from typing import Optional

class UpdateUser(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

@app.patch("/users/{old_email}")
def update_user(old_email: str, user: UpdateUser):

    

    user_exist = db.query(User).filter(User.email == old_email).first()

    if user_exist is None:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.name is not None:
        user_exist.name = user.name

    if user.email is not None:
        user_exist.email = user.email

    if user.password is not None:
        user_exist.password = user.password

    db.commit()

    db.refresh(user_exist)

    db.close()

    return {
        "message": "User updated successfully",
        "data": user_exist
    }
