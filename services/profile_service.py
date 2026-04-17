from datetime import datetime, timezone
from uuid import uuid4

from clients.genderize import get_gender
from clients.agify import get_age
from clients.nationalize import get_country
from models import Profile


def age_group(age: int):
    if age <= 12:
        return "child"
    if age <= 19:
        return "teenager"
    if age <= 59:
        return "adult"
    return "senior"


async def build_profile(db, name: str):

    name = name.strip().lower()

    existing = db.query(Profile).filter(Profile.name == name).first()
    if existing:
        return {"type": "exists", "data": existing}

    g = await get_gender(name)
    a = await get_age(name)
    n = await get_country(name)

    # STRICT VALIDATION (HNG RULES)
    if not g.get("gender") or g.get("count", 0) == 0:
        return {"type": "error", "api": "Genderize"}

    if a.get("age") is None:
        return {"type": "error", "api": "Agify"}

    countries = n.get("country", [])
    if not countries:
        return {"type": "error", "api": "Nationalize"}

    top = max(countries, key=lambda x: x["probability"])

    profile = Profile(
      id = str(uuid4()),
        name=name,

        gender=g["gender"],
        gender_probability=g["probability"],
        sample_size=g["count"],

        age=a["age"],
        age_group=age_group(a["age"]),

        country_id=top["country_id"],
        country_probability=top["probability"],

        created_at=datetime.now(timezone.utc)
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return {"type": "created", "data": profile}