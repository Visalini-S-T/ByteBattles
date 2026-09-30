from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..schemas.user import (
    UserCreate,
    UserResponse,
    RefreshAccessTokenRequest,
    TokenPayload,
    AdminBootstrapRequest
)

from ..utils import password_manager, oauth2
from ..database import get_db

from shared.models import User, UserType

from config import DUMMY_PASS

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

DUMMY_PASSWORD = password_manager.hash(DUMMY_PASS)

@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(new_user: UserCreate, db: Session = Depends(get_db)):

    if (new_user.password != new_user.conf_password):
        raise HTTPException(detail="confirm password and given password don't match", status_code=status.HTTP_400_BAD_REQUEST)

    user = db.query(User).filter(User.username == new_user.username).first()
    if not user:
        user = db.query(User).filter(User.email == new_user.email).first()
    
    if user:
        raise HTTPException(detail="user with this username or email already exists", status_code=status.HTTP_409_CONFLICT)
    
    hashed_password = password_manager.hash(new_user.password)
    new_user = User(username=new_user.username, email=new_user.email, password_hash=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
@router.post('/login', status_code=status.HTTP_200_OK)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        raise HTTPException(
            detail="Incorrect username or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not password_manager.verify(form_data.password, user.password_hash):
        raise HTTPException(
            detail="Incorrect username or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"}
        )

    token_payload = TokenPayload(sub=user.id)

    access_token = oauth2.create_access_token(token_payload)
    refresh_token = oauth2.create_refresh_token(token_payload)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post('/bootstrap-admin', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def bootstrap_admin(details: AdminBootstrapRequest, db: Session = Depends(get_db)):
    admin_exists = db.query(User).filter(
        User.user_type == UserType.ADMIN
    ).first()

    if admin_exists:
        raise HTTPException(
            detail="An admin already exists",
            status_code=status.HTTP_403_FORBIDDEN
        )

    if details.password != details.conf_password:
        raise HTTPException(
            detail="confirm password and given password don't match",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    existing_user = db.query(User).filter(
        (User.username == details.username) |
        (User.email == details.email)
    ).first()

    if existing_user:
        raise HTTPException(
            detail="user with this username or email already exists",
            status_code=status.HTTP_409_CONFLICT
        )

    hashed_password = password_manager.hash(details.password)

    admin = User(
        username=details.username,
        email=details.email,
        password_hash=hashed_password,
        user_type=UserType.ADMIN
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin

@router.post('/refresh', status_code=status.HTTP_200_OK)
def refresh(token: RefreshAccessTokenRequest):
    refresh_token = token.refresh_token
    access_token = oauth2.refresh_access_token(refresh_token)
    return {
        "access_token": access_token
    }
