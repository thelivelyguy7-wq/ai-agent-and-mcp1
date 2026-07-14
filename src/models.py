from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Review(BaseModel):
    id: Optional[str] = None
    text: str = Field(..., min_length=1, description="The content of the review")
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    date: datetime = Field(..., description="Date the review was posted")
    title: Optional[str] = None
    language: Optional[str] = Field(default="en", description="Language code")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "12345",
                "text": "Great app, highly recommend!",
                "rating": 5,
                "date": "2023-10-25T14:30:00Z",
                "title": "Awesome",
                "language": "en"
            }
        }
