from pydantic import BaseModel, Field


# ---------------- REQUEST ----------------
class ProfileRequest(BaseModel):
    name: str = Field(..., min_length=1)


# ---------------- RESPONSE DATA OBJECT ----------------
class ProfileData(BaseModel):
    id: str
    name: str

    gender: str
    gender_probability: float
    sample_size: int

    age: int
    age_group: str

    country_id: str
    country_probability: float

    created_at: str


# ---------------- CREATE RESPONSE ----------------
class CreateProfileResponse(BaseModel):
    status: str
    data: ProfileData


# ---------------- EXISTING PROFILE RESPONSE ----------------
class ExistingProfileResponse(BaseModel):
    status: str
    message: str
    data: ProfileData


# ---------------- LIST RESPONSE ITEM ----------------
class ProfileListItem(BaseModel):
    id: str
    name: str
    gender: str
    age: int
    age_group: str
    country_id: str