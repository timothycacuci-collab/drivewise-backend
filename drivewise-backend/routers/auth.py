from fastapi import APIRouter, HTTPException, Depends, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from database import get_db, User
import uuid
import os
from itsdangerous import URLSafeTimedSerializer

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "drivewise-secret-key-change-in-production")
serializer = URLSafeTimedSerializer(SECRET_KEY)
SESSION_COOKIE = "drivewise_session"

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        user_id = serializer.loads(token, max_age=60 * 60 * 24 * 7)  # 7 days
    except Exception:
        raise HTTPException(status_code=401, detail="Session expired")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def set_session(response: Response, user_id: str):
    token = serializer.dumps(user_id)
    response.set_cookie(
        SESSION_COOKIE, token,
        httponly=True, samesite="lax",
        secure=os.getenv("ENV", "dev") == "production",
        max_age=60 * 60 * 24 * 7
    )

@router.post("/register")
def register(body: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        id=str(uuid.uuid4()),
        name=body.name,
        email=body.email,
        hashed_password=pwd_context.hash(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    set_session(response, user.id)
    return {"id": user.id, "name": user.name, "email": user.email}

@router.post("/login")
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not pwd_context.verify(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    set_session(response, user.id)
    return {"id": user.id, "name": user.name, "email": user.email}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE)
    return {"ok": True}

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "email": user.email}
