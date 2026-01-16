from pydantic import BaseModel
from typing import Optional

class BookingData(BaseModel):
    attractionId: int
    date: str
    time: str
    price: int

class BookingAttraction(BaseModel):
    id: int
    name: str
    address: str
    image: str

class Booking(BaseModel):
    attraction: Optional[BookingAttraction]
    date: Optional[str]
    time: Optional[str]
    price: Optional[int]