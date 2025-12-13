from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from contextlib import asynccontextmanager
import csv
import io

from database import engine, get_db, Base
from models import Image, Vote

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
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

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VoteRequest(BaseModel):
    image_id: int
    vote_type: str


class ImageResponse(BaseModel):
    id: int
    url: str
    likes: int
    dislikes: int

@app.get("/images", response_model=list[ImageResponse])
def get_images(db: Session = Depends(get_db)):
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
    if vote.vote_type not in ["like", "dislike"]:
        raise HTTPException(status_code=400, detail="Invalid vote type")

    image = db.query(Image).filter(Image.id == vote.image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    new_vote = Vote(image_id=vote.image_id, vote_type=vote.vote_type)
    db.add(new_vote)
    db.commit()

    return {"message": "Vote recorded successfully"}


@app.get("/export-votes")
def export_votes(db: Session = Depends(get_db)):
    images = db.query(Image).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["image_id", "url", "likes", "dislikes"])

    for image in images:
        likes = (
            db.query(func.count(Vote.id))
            .filter(Vote.image_id == image.id, Vote.vote_type == "like")
            .scalar() or 0
        )
        dislikes = (
            db.query(func.count(Vote.id))
            .filter(Vote.image_id == image.id, Vote.vote_type == "dislike")
            .scalar() or 0
        )
        writer.writerow([image.id, image.url, likes, dislikes])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=votes.csv"},
    )