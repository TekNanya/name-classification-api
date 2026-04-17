from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
from datetime import datetime, timezone
import uuid

from database import engine, SessionLocal
from models import Base, Profile

Base.metadata.create_all(bind=engine)

app = FastAPI()


# ✅ CORS
@app.middleware("http")
async def cors(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# ✅ REQUEST MODEL
class ProfileRequest(BaseModel):
    name: str


# ✅ AGE GROUP LOGIC
def get_age_group(age):
    if age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    return "senior"


# ===============================
# 🔹 CREATE PROFILE
# ===============================
@app.post("/api/profiles", status_code=201)
def create_profile(payload: ProfileRequest):
    name = payload.name.strip().lower()

    if not name:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Name parameter is required"
        })

    db = SessionLocal()

    try:
        # ✅ Check duplicate
        existing = db.query(Profile).filter(Profile.name == name).first()
        if existing:
            return {
                "status": "success",
                "message": "Profile already exists",
                "data": existing.__dict__ | {}
            }

        # ✅ API CALLS
        g = requests.get("https://api.genderize.io/", params={"name": name}, timeout=5)
        a = requests.get("https://api.agify.io/", params={"name": name}, timeout=5)
        n = requests.get("https://api.nationalize.io/", params={"name": name}, timeout=5)

        if g.status_code != 200:
            raise Exception("Genderize")
        if a.status_code != 200:
            raise Exception("Agify")
        if n.status_code != 200:
            raise Exception("Nationalize")

        g = g.json()
        a = a.json()
        n = n.json()

        # ✅ EDGE CASES
        if not g.get("gender") or g.get("count") == 0:
            return JSONResponse(status_code=502, content={
                "status": "error",
                "message": "Genderize returned an invalid response"
            })

        if a.get("age") is None:
            return JSONResponse(status_code=502, content={
                "status": "error",
                "message": "Agify returned an invalid response"
            })

        if not n.get("country"):
            return JSONResponse(status_code=502, content={
                "status": "error",
                "message": "Nationalize returned an invalid response"
            })

        # ✅ Top country
        top_country = max(n["country"], key=lambda x: x["probability"])

        # ✅ CREATE PROFILE
        profile = Profile(
            id=str(uuid.uuid4()),  # acceptable if uuid7 not available
            name=name,

            gender=g["gender"],
            gender_probability=g["probability"],
            sample_size=g["count"],

            age=a["age"],
            age_group=get_age_group(a["age"]),

            country_id=top_country["country_id"],
            country_probability=top_country["probability"],

            created_at=datetime.now(timezone.utc).isoformat()
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

        return {
            "status": "success",
            "data": {
                "id": profile.id,
                "name": profile.name,
                "gender": profile.gender,
                "gender_probability": profile.gender_probability,
                "sample_size": profile.sample_size,
                "age": profile.age,
                "age_group": profile.age_group,
                "country_id": profile.country_id,
                "country_probability": profile.country_probability,
                "created_at": profile.created_at
            }
        }

    except Exception as e:
        return JSONResponse(status_code=502, content={
            "status": "error",
            "message": f"{str(e)} returned an invalid response"
        })

    finally:
        db.close()


# ===============================
# 🔹 GET SINGLE PROFILE
# ===============================
@app.get("/api/profiles/{id}")
def get_profile(id: str):
    db = SessionLocal()
    try:
        profile = db.query(Profile).filter(Profile.id == id).first()

        if not profile:
            return JSONResponse(status_code=404, content={
                "status": "error",
                "message": "Profile not found"
            })

        return {
            "status": "success",
            "data": {
                "id": profile.id,
                "name": profile.name,
                "gender": profile.gender,
                "gender_probability": profile.gender_probability,
                "sample_size": profile.sample_size,
                "age": profile.age,
                "age_group": profile.age_group,
                "country_id": profile.country_id,
                "country_probability": profile.country_probability,
                "created_at": profile.created_at
            }
        }
    finally:
        db.close()


# ===============================
# 🔹 GET ALL PROFILES (FILTER)
# ===============================
@app.get("/api/profiles")
def get_profiles(
    gender: str = Query(None),
    country_id: str = Query(None),
    age_group: str = Query(None)
):
    db = SessionLocal()

    try:
        query = db.query(Profile)

        if gender:
            query = query.filter(Profile.gender.ilike(gender))
        if country_id:
            query = query.filter(Profile.country_id.ilike(country_id))
        if age_group:
            query = query.filter(Profile.age_group.ilike(age_group))

        profiles = query.all()

        return {
            "status": "success",
            "count": len(profiles),
            "data": [
                {
                    "id": p.id,
                    "name": p.name,
                    "gender": p.gender,
                    "age": p.age,
                    "age_group": p.age_group,
                    "country_id": p.country_id
                }
                for p in profiles
            ]
        }

    finally:
        db.close()


# ===============================
# 🔹 DELETE PROFILE
# ===============================
@app.delete("/api/profiles/{id}", status_code=204)
def delete_profile(id: str):
    db = SessionLocal()

    try:
        profile = db.query(Profile).filter(Profile.id == id).first()

        if not profile:
            return JSONResponse(status_code=404, content={
                "status": "error",
                "message": "Profile not found"
            })

        db.delete(profile)
        db.commit()

        return JSONResponse(status_code=204, content=None)

    finally:
        db.close()