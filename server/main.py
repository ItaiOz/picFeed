from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
import csv
import io

from database import engine, get_db, Base
from models import Image, Vote

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VoteRequest(BaseModel):
    image_id: int
    vote_type: str  # 'like' or 'dislike'


class ImageResponse(BaseModel):
    id: int
    url: str
    likes: int
    dislikes: int


@app.on_event("startup")
def seed_database():
    """Seed database with 100 images on startup if not already seeded"""
    db = next(get_db())
    try:
        existing_count = db.query(Image).count()
        if existing_count == 0:
            images = [
                Image(id=i, url=f"https://picsum.photos/id/{i}/400/300")
                for i in range(1, 101)
            ]
            db.bulk_save_objects(images)
            db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/images", response_model=list[ImageResponse])
def get_images(db: Session = Depends(get_db)):
    """Get all images with their vote counts"""
    images = db.query(Image).all()

    result = []
    for image in images:
        likes = (
            db.query(func.count(Vote.id))
            .filter(Vote.image_id == image.id, Vote.vote_type == "like")
            .scalar()
        )
        dislikes = (
            db.query(func.count(Vote.id))
            .filter(Vote.image_id == image.id, Vote.vote_type == "dislike")
            .scalar()
        )
        result.append(
            ImageResponse(
                id=image.id, url=image.url, likes=likes or 0, dislikes=dislikes or 0
            )
        )

    return result


@app.post("/vote")
def create_vote(vote: VoteRequest, db: Session = Depends(get_db)):
    """Create a new vote (like or dislike)"""
    if vote.vote_type not in ["like", "dislike"]:
        raise HTTPException(status_code=400, detail="Invalid vote type")

    # Check if image exists
    image = db.query(Image).filter(Image.id == vote.image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Create vote
    new_vote = Vote(image_id=vote.image_id, vote_type=vote.vote_type)
    db.add(new_vote)
    db.commit()

    return {"message": "Vote recorded successfully"}


@app.get("/export")
def export_votes(db: Session = Depends(get_db)):
    """Export all votes to CSV"""
    votes = db.query(Vote).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["Vote ID", "Image ID", "Vote Type", "Created At"])

    # Write data
    for vote in votes:
        writer.writerow([vote.id, vote.image_id, vote.vote_type, vote.created_at])

    # Return CSV response
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=votes.csv"},
    )