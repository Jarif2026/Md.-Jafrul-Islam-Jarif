from typing import Literal
from pydantic import BaseModel, Field


class MovieCreate(BaseModel):
    movie_id: int
    title: str
    director: str
    genre: Literal["action", "comedy", "drama", "thriller"]
    duration: int = Field(..., gt=0)
    rating: float = Field(..., ge=0.0, le=5.0)


class MovieUpdate(BaseModel):
    title: str
    director: str
    genre: Literal["action", "comedy", "drama", "thriller"]
    duration: int = Field(..., gt=0)
    rating: float = Field(..., ge=0.0, le=5.0)