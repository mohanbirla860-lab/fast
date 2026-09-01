
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext

# ==========================
# FastAPI App
# ==========================

app = FastAPI()

# ==========================
# MySQL Connection
# ==========================

DATABASE_URL = "mysql+pymysql://root:Mohan%40123@localhost:3306/college"


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

db = SessionLocal()

# PASSWORD HASHING ///

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# ==========================
# JWT Configuration
# ==========================

SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ==========================
# Database Model
# ==========================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100))

    email = Column(String(100), unique=True)

    password = Column(String(100))

    role = Column(String(100))

Base.metadata.create_all(bind=engine)



# ==========================
# Pydantic Schemas
# ==========================

class RegisterUser(BaseModel):

    name: str

    email: str

    password: str

    role : str


class LoginUser(BaseModel):

    email: str

    password: str

# ==========================
# Create JWT
# ==========================

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {
            "exp": expire
        }
    )

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

# ==========================
# Verify JWT
# ==========================

def get_current_user(token: str = Depends(oauth2_scheme)):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if email is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid Token"
            )

        db_user = db.query(User).filter(
            User.email == email
        ).first()

        if db_user is None:

            raise HTTPException(
                status_code=404,
                detail="User Not Found"
            )

        return db_user

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

# ==========================
# Register API
# ==========================

@app.post("/register")

def register(user: RegisterUser):

    check_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if check_user:

        raise HTTPException(
            status_code=400,
            detail="Email Already Exists"
        )
    
    # Hash Password
    hashed_password = pwd_context.hash(user.password)


    new_user = User(

        name=user.name,

        email=user.email,

        password=hashed_password,

        role = user.role

    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {

        "message": "User Registered",

        "data": new_user

    }

# ==========================
# Login API
# ==========================

@app.post("/login")

def login(user: LoginUser):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if db_user is None:

        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=401,
            detail="Wrong Password"
        )

    token = create_access_token(

        {

            "sub": db_user.email,
            "role": db_user.role

        }

    )

    return {

        "access_token": token,

        "token_type": "Bearer"

    }

# ==========================
# Protected Profile API
# ==========================

@app.get("/profile")

def profile(current_user: User = Depends(get_current_user)):

    if current_user.role != "admin":
        raise HTTPException( 
            status_code=403,
        )
    return {

        "id": current_user.id,

        "name": current_user.name,

        "email": current_user.email,

        "role": current_user.role

    }

