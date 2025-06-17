from sqlalchemy.orm import Session
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# In auth.py - Ensure new users start unapproved
def register_user(db: Session, username: str, password: str):
    hashed = get_password_hash(password)
    user = User(
        username=username, 
        hashed_password=hashed,
        is_approved=False,  # Default to unapproved
        is_admin=False      # Default to regular user
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password) and user.is_approved:
        return user
    return None
