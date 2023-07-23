# main.py
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import secrets

URL = '127.0.0.1:8000'

from utils_email import send_verify_email
# Initialize FastAPI app
app = FastAPI()

db_file = "e_test1.db"

# Create the SQLite database engine
engine = create_engine(f"sqlite:///{db_file}", future=True)

# Create the database engine
# engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


# Database Model for Verification
class Verification(Base):
    __tablename__ = "verifications"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    token = Column(String, unique=True, index=True)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create the database tables
Verification.metadata.create_all(bind=engine)


# Database Model for User
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create the database tables
User.metadata.create_all(bind=engine)


def create_verification_token(db, email: str):
    token = secrets.token_urlsafe(32)
    db_verification = Verification(email=email, token=token)
    db.add(db_verification)
    db.commit()
    db.refresh(db_verification)  # Refresh the instance to ensure it's bound to the session
    return db_verification


def get_verification_by_token(db, token: str):
    return db.query(Verification).filter(Verification.token == token).one_or_none()


def create_user(db, email: str, password: str):
    db_user = User(email=email, password=password)
    db.add(db_user)
    db.commit()
    return db_user


def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).one_or_none()


@app.get("/verify/{token}")
def verify_token(token: str):
    with SessionLocal() as conn:
        verification = get_verification_by_token(conn, token)
        if not verification or verification.is_used:
            raise HTTPException(status_code=404, detail="Token not found or already used.")
        verification.is_used = True
        conn.commit()
    return {"message": "Email verification successful!"}


@app.get("/generate_verification/{email}")
def generate_verification(email: str):
    with SessionLocal() as conn:
        existing_verification = get_verification_by_token(conn, email)
        if existing_verification:
            raise HTTPException(status_code=400, detail="Email is already verified.")
        
        # Create a new verification entry in the database
        verification = create_verification_token(conn, email)

    verification_link = f"http://{URL}/verify/{verification.token}"
    send_verification_email(email, verification_link)

    return {"message": "Verification email sent successfully", "email": email}


@app.post("/signup/")
def sign_up(email: str, password: str):
    with SessionLocal() as conn:
        existing_user = get_user_by_email(conn, email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered.")

        # Create a new user
        user = create_user(conn, email, password)

        # Create a verification entry in the database and send the verification email
        verification = create_verification_token(conn, email)

    verification_link = f"http://{URL}/verify/{verification.token}"
    send_verification_email(email, verification_link)

    return {"message": "Sign up successful. Verification email sent.", "email": email}


def send_verification_email(email, verification_link):
    # Replace these with your email settings
    # ...

    # Email content
    subject = "Email Verification"
    # body = f"Click the following link to verify your email: {verification_link}"

    try:
        send_verify_email(email_receiver=email, v_link=verification_link)
        # Create the email message
        # ...

    except Exception as e:
        print("Failed to send email:", str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
