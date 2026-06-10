from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId

from app.database import users_collection
from app.schemas import UserRegister, UserLogin, TokenResponse
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

def public_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
    }

@router.post("/register", response_model=TokenResponse)
async def register(payload: UserRegister):
    existing = await users_collection.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user_doc = {
        "name": payload.name,
        "email": payload.email.lower(),
        "password": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc),
    }
    result = await users_collection.insert_one(user_doc)
    user_doc["_id"] = ObjectId(result.inserted_id)
    token = create_access_token(str(result.inserted_id))
    return {"access_token": token, "user": public_user(user_doc)}

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    user = await users_collection.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong email or password")

    token = create_access_token(str(user["_id"]))
    return {"access_token": token, "user": public_user(user)}
