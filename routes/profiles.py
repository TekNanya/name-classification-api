from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db import SessionLocal
from models import Profile
from services.profile_service import build_profile

router = APIRouter(prefix="/api/profiles")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- CREATE ----------------
@router.post("", status_code=201)
async def create_profile(payload: dict, db: Session = Depends(get_db)):

    result = await build_profile(db, payload["name"])

    if result["type"] == "exists":
        p = result["data"]
        return {
            "status": "success",
            "message": "Profile already exists",
            "data": {
                "id": p.id,
                "name": p.name,
                "gender": p.gender,
                "gender_probability": p.gender_probability,
                "sample_size": p.sample_size,
                "age": p.age,
                "age_group": p.age_group,
                "country_id": p.country_id,
                "country_probability": p.country_probability,
                "created_at": p.created_at.isoformat()
            }
        }

    if result["type"] == "error":
        return {
            "status": "error",
            "message": f'{result["api"]} returned an invalid response'
        }

    p = result["data"]

    return {
        "status": "success",
        "data": {
            "id": p.id,
            "name": p.name,
            "gender": p.gender,
            "gender_probability": p.gender_probability,
            "sample_size": p.sample_size,
            "age": p.age,
            "age_group": p.age_group,
            "country_id": p.country_id,
            "country_probability": p.country_probability,
            "created_at": p.created_at.isoformat()
        }
    }


# ---------------- GET ONE ----------------
@router.get("/{id}")
def get_profile(id: str, db: Session = Depends(get_db)):

    p = db.query(Profile).filter(Profile.id == id).first()

    if not p:
        return {"status": "error", "message": "Profile not found"}

    return {
        "status": "success",
        "data": {
            "id": p.id,
            "name": p.name,
            "gender": p.gender,
            "gender_probability": p.gender_probability,
            "sample_size": p.sample_size,
            "age": p.age,
            "age_group": p.age_group,
            "country_id": p.country_id,
            "country_probability": p.country_probability,
            "created_at": p.created_at.isoformat()
        }
    }


# ---------------- GET ALL ----------------
@router.get("")
def get_profiles(
    gender: str = Query(None),
    country_id: str = Query(None),
    age_group: str = Query(None),
    db: Session = Depends(get_db)
):

    q = db.query(Profile)

    if gender:
        q = q.filter(Profile.gender == gender.lower())
    if country_id:
        q = q.filter(Profile.country_id == country_id.upper())
    if age_group:
        q = q.filter(Profile.age_group == age_group.lower())

    results = q.all()

    return {
        "status": "success",
        "count": len(results),
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "gender": p.gender,
                "age": p.age,
                "age_group": p.age_group,
                "country_id": p.country_id
            }
            for p in results
        ]
    }


# ---------------- DELETE ----------------
@router.delete("/{id}", status_code=204)
def delete_profile(id: str, db: Session = Depends(get_db)):

    p = db.query(Profile).filter(Profile.id == id).first()

    if not p:
        return {"status": "error", "message": "Profile not found"}

    db.delete(p)
    db.commit()

    return None