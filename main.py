from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
import shutil

from database import SessionLocal, engine
from models import Base, User, File as FileModel
from auth import hash_password, verify_password, create_access_token, decode_access_token
from s3_utils import create_presigned_post, create_presigned_put_url

Base.metadata.create_all(bind=engine)

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    user = get_user(db, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.post("/signup")
def signup(username: str, password: str, db: Session = Depends(get_db)):
    if get_user_by_username(db, username):
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=username, password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = create_access_token({"sub": user.id})
    return {"message": "User created", "access_token": access_token}


@app.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/upload")
def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_db = FileModel(filename=file.filename, owner_id=current_user.id)
    db.add(file_db)
    db.commit()
    db.refresh(file_db)

    return {"message": "File uploaded", "file_id": file_db.id}


@app.get("/files/me")
def list_my_files(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    files = db.query(FileModel).filter(FileModel.owner_id == current_user.id).all()
    return files


@app.post("/s3/presign")
def s3_presign(filename: str, current_user: User = Depends(get_current_user)):
    bucket = os.environ.get("S3_BUCKET")
    if not bucket:
        raise HTTPException(status_code=500, detail="S3_BUCKET not configured")
    key = f"{current_user.id}/{filename}"
    # Return a presigned POST form that clients can use to upload directly to S3
    form = create_presigned_post(bucket, key)
    return {"bucket": bucket, "key": key, "form": form}


@app.get("/s3/presign_put")
def s3_presign_put(filename: str, current_user: User = Depends(get_current_user)):
    bucket = os.environ.get("S3_BUCKET")
    if not bucket:
        raise HTTPException(status_code=500, detail="S3_BUCKET not configured")
    key = f"{current_user.id}/{filename}"
    url = create_presigned_put_url(bucket, key)
    return {"bucket": bucket, "key": key, "put_url": url}


if __name__ == "__main__":
    try:
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
    except Exception as e:
        print("Failed to start server. Make sure dependencies are installed (uvicorn, fastapi, etc.).")
        print("Error:", e)
        raise
