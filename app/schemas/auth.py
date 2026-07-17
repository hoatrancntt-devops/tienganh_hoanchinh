import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(default="", max_length=120)
    goal: str = Field(default="speaking", pattern="^(speaking|reading)$")
    daily_goal_minutes: int = Field(default=10, ge=5, le=60)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    role: str
    timezone: str


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cefr_level_current: str
    goal: str
    daily_goal_minutes: int
    reminder_hour: int
    email_opt_in: bool
    streak_days: int
