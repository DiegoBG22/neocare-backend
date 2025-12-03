from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token
from auth_handler import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Endpoint para registrar un nuevo usuario"""
    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Crear nuevo usuario
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully"}

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Endpoint para iniciar sesión y obtener token JWT"""
    # Buscar usuario por email
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verificar contraseña
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Crear token de acceso
    access_token = create_access_token(user_id=user.id)
    
    return Token(access_token=access_token)
