from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from core.security import get_password_hash, verify_password, create_access_token
from schemas.token import Token

router = APIRouter(tags=["authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    ign: str
    store_password: bool = False
    ms_credentials: str = None
    is_admin: bool = False

@router.post("/login")
async def login_user(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    email = request.email
    password = request.password
    ign = request.ign
    store_password = request.store_password
    ms_credentials = request.ms_credentials
    # Check if user already exists
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if IGN already exists
    if db.query(User).filter(User.ign == ign).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IGN already registered"
        )

    # Create new user
    hashed_password = get_password_hash(password)
    encrypted_ms = None
    if store_password and ms_credentials:
        from core.security import encrypt_data
        encrypted_ms = encrypt_data(ms_credentials)
        
    user = User(
        email=email,
        hashed_password=hashed_password,
        ign=ign,
        store_password=store_password,
        encrypted_ms_credentials=encrypted_ms,
        is_admin=request.is_admin
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "User created successfully"}
