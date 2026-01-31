from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    # CSV of user ids who have access; for small-scale sharing this is acceptable
    shared_with = Column(String, nullable=True)
    storage_key = Column(String, nullable=True)
