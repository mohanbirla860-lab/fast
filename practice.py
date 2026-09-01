from fastapi import FastAPI,HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine,String, Column, Integer, Index
from sqlalchemy.orm import declarative_base, sessionmaker,Session
from passlib.context import CryptContext
# jwt lib
from jose import jwt, JWSError
from datetime import datetime, timedelta

app = FastAPI()

DATABASE_URL = "mysql+pymysql://root:Mohan%40123@localhost:3306/college"

engine = create_engine(DATABASE_URL)

Sessionmysql = sessionmaker(blind = engine)

db = Sessionmysql()

Base = declarative_base()

class User(Base):

    __tablename__ = "users"

    id = Column(Integer,primary_key = True, index = True)
    name = Column(String(100))
    email = Column(String(100))
    password = Column(String(100))
    role = Column(String(100))

    Base.metadata.create_all(blind = engine)


# password hashing

pwd_hashing = CryptContext(
    schemes = ["bcrypt"],
    deprecate = "auto"
)

def hash_password(password :str):
    return pwd_hashing.hash(password)

def verify_password(plain_password:str, hash_password:str):
    return pwd_hashing.verify(plain_password , hash_password)

# generate tokens jwt:

SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def generate_token(data : dict):

    to_encode = data.copy()
    
    expire = datetime.utcnow()+ timedelta(minute = ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update(
        {
        "expire" : expire
 }   )

    Token = jwt.encode(
        SECRET_KEY,
        to_encode,
        algorithm= ALGORITHM
    )

    return Token

# varification jwt token 

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

def current_user(token :str = Depends(oauth2_schema)):

    payload = jwt.decode(
        SECRET_KEY,
        token,
        algorithms= ALGORITHM

    )

    email = payload.get("sub")

    if email is None:
        raise HTTPException(
            error = 401,
            detail = "Invalid token"
        )

    user_db = db.query(User).filter(User.email == email)

    if user_db is None:
        raise HTTPException(
            error = 401,
            detail = "user not found"
        )
    
    return user_db

    






app = FastAPI()


# pydantic validation
# sign up
class UserDTO(BaseModel):
    name: str
    email : str
    password : str


# login

class Login(BaseModel):
    email : str
    password : str

# signup api

@app.post("/signup")
     
def create_user(user : UserDTO):

    email_exist = db.query(User).filter(db.email == user.email).first()

    if email_exist :
      raise HTTPException(
          error = 400,
          detail = "email not exist"
      )
    
    db.add()

    db.commit()

    db.close()
    
    return {
        "message": "USER CREATED SUCCESSFULLY"
    }

@app.post("/login")
def login(user : Login):

     cheak_email = db.query(user).filter(db.email == user.email )

     if 



    