"""
Integration tests for the PicsFeed API.
These tests use a real PostgreSQL database in Docker to test full API workflows.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from database import Base, get_db
from main import app
from models import Image, Vote

DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://picsfeed:picsfeed@localhost:5432/picsfeed_test"
)

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


class TestImageEndpoints:
    
    def test_get_images_returns_empty_list_initially(self, db_session):
        response = client.get("/images")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_images_with_vote_counts(self, db_session):
        image1 = Image(id=1, url="https://example.com/1.jpg")
        image2 = Image(id=2, url="https://example.com/2.jpg")
        db_session.add_all([image1, image2])
        db_session.commit()
        
        vote1 = Vote(image_id=1, vote_type="like")
        vote2 = Vote(image_id=1, vote_type="like")
        vote3 = Vote(image_id=1, vote_type="dislike")
        vote4 = Vote(image_id=2, vote_type="like")
        db_session.add_all([vote1, vote2, vote3, vote4])
        db_session.commit()
        
        response = client.get("/images")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 2
        img1_data = next(img for img in data if img["id"] == 1)
        assert img1_data["likes"] == 2
        assert img1_data["dislikes"] == 1
        
        img2_data = next(img for img in data if img["id"] == 2)
        assert img2_data["likes"] == 1
        assert img2_data["dislikes"] == 0


class TestVoteEndpoints:
    
    def test_vote_like_on_image(self, db_session):
        image = Image(id=1, url="https://example.com/1.jpg")
        db_session.add(image)
        db_session.commit()
        
        response = client.post("/vote", json={"image_id": 1, "vote_type": "like"})
        assert response.status_code == 200
        assert response.json()["message"] == "Vote recorded"
        
        votes = db_session.query(Vote).filter(Vote.image_id == 1).all()
        assert len(votes) == 1
        assert votes[0].vote_type == "like"
    
    def test_vote_dislike_on_image(self, db_session):
        image = Image(id=1, url="https://example.com/1.jpg")
        db_session.add(image)
        db_session.commit()
        
        response = client.post("/vote", json={"image_id": 1, "vote_type": "dislike"})
        assert response.status_code == 200
        
        votes = db_session.query(Vote).filter(Vote.image_id == 1).all()
        assert len(votes) == 1
        assert votes[0].vote_type == "dislike"
    
    def test_vote_on_nonexistent_image(self, db_session):
        response = client.post("/vote", json={"image_id": 999, "vote_type": "like"})
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_invalid_vote_type(self, db_session):
        image = Image(id=1, url="https://example.com/1.jpg")
        db_session.add(image)
        db_session.commit()
        
        response = client.post("/vote", json={"image_id": 1, "vote_type": "invalid"})
        assert response.status_code == 400
    
    def test_multiple_votes_workflow(self, db_session):
        images = [
            Image(id=i, url=f"https://example.com/{i}.jpg")
            for i in range(1, 6)
        ]
        db_session.add_all(images)
        db_session.commit()
        
        votes_data = [
            {"image_id": 1, "vote_type": "like"},
            {"image_id": 1, "vote_type": "like"},
            {"image_id": 2, "vote_type": "dislike"},
            {"image_id": 3, "vote_type": "like"},
            {"image_id": 3, "vote_type": "like"},
            {"image_id": 3, "vote_type": "like"},
        ]
        
        for vote_data in votes_data:
            response = client.post("/vote", json=vote_data)
            assert response.status_code == 200
        
        response = client.get("/images")
        assert response.status_code == 200
        data = response.json()
        
        vote_counts = {img["id"]: (img["likes"], img["dislikes"]) for img in data}
        assert vote_counts[1] == (2, 0)
        assert vote_counts[2] == (0, 1)
        assert vote_counts[3] == (3, 0)
        assert vote_counts[4] == (0, 0)
        assert vote_counts[5] == (0, 0)


class TestExportEndpoint:
    
    def test_export_votes_csv(self, db_session):
        image1 = Image(id=1, url="https://example.com/1.jpg")
        image2 = Image(id=2, url="https://example.com/2.jpg")
        db_session.add_all([image1, image2])
        db_session.commit()
        
        vote1 = Vote(image_id=1, vote_type="like")
        vote2 = Vote(image_id=2, vote_type="dislike")
        db_session.add_all([vote1, vote2])
        db_session.commit()
        
        response = client.get("/export-votes")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        
        csv_content = response.text
        lines = csv_content.strip().split("\n")
        assert lines[0] == "image_id,url,likes,dislikes"
        assert len(lines) == 3
    
    def test_export_empty_votes(self, db_session):
        response = client.get("/export-votes")
        assert response.status_code == 200
        
        csv_content = response.text
        lines = csv_content.strip().split("\n")
        assert lines[0] == "image_id,url,likes,dislikes"
        assert len(lines) == 1
