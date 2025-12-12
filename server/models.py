from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Image(Base):
    """Model for storing images"""

    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Vote(Base):
    """Model for storing votes (likes/dislikes)"""

    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    vote_type = Column(String(10), nullable=False)  # 'like' or 'dislike'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
