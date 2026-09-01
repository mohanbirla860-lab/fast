from fastapi import FastAPI
from fastapi import HTTPException
from pymongo import MongoClient
from pydantic import BaseModel

app = FastAPI()

client = MongoClient("mongodb+srv://mohanbirla860_db_user:dSExgkPGPDy3r0h5@cluster0.ah9lg8p.mongodb.net/?appName=Cluster0")
db = client["mydatabase"]
users = db["users"]

class UserDTO(BaseModel):
    name: str
    email: str
    password: str

@app.post("/signup")
def signup(user: UserDTO):

    existing_user = users.find_one({"email": user.email})

    if existing_user:
        return {"message": "email is already exists please!! Try another email"}

    users.insert_one(user.model_dump())
    return {"message": "User created successfully"}

# GET api
@app.get("/users")
def get_users():

    data = list(users.find({}, {"_id": 0}))

    return data

# show one users profile on the basis of emailid



@app.get("/users/{email}")
def get_user(email: str):

    user = users.find_one({"email": email})

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user["_id"] = str(user["_id"])

    return user

# POST login api

@app.post("/login")
def login(user: UserDTO):

    existing = users.find_one(
        {
            "email": user.email,
            "password": user.password
        }
    )

    if existing:
        return {"message": "Login Successful"}

    return {"message": "Invalid Email or Password"} 

# update using put method user profile



class UpdateUser(BaseModel):
    name: str
    email: str


@app.put("/users/{old_email}")
def update_user(old_email: str, user: UpdateUser):

    # Check if user exists
    existing_user = users.find_one({"email": old_email})

    if not existing_user:
        return {"message": "User not found"}

    # Check if new email is already used by another user
    email_exists = users.find_one({"email": user.email})

    if email_exists and user.email != old_email:
        return {"message": "Email already exists"}

    # Update name and email
    users.update_one(
        {"email": old_email},
        {
            "$set": {
                "name": user.name,
                "email": user.email
            }
        }
    )

    return {"message": "Profile updated successfully"}

@app.delete("/users/{email}")
def delete_user(email: str):

    result = users.delete_one({"email": email})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "User deleted successfully"
    }