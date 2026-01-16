from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from models.booking import BookingAttraction

class OrderInput(BaseModel):
    price: int
    trip:Trip
    contact: Contact

class CreateOrderData(BaseModel):
    prime: str
    order: OrderInput

class Trip(BaseModel):
    attraction: BookingAttraction
    date: str # 2022-01-31
    time: str # afternoon

class Order(BaseModel):
    number: str # 20210425121135(訂單編號)
    price: int
    trip: Trip
    contact: Contact
    status: Literal[0, 1] = Field(default=1, description="支付狀態: 0 為失敗, 1 為成功")

class Contact(BaseModel):
    name: str
    email: EmailStr
    phone: str

class OrderResult(BaseModel):
    number: str # 20210425121135(訂單編號)
    payment: PaymentStatus

class PaymentStatus(BaseModel):
    status: Literal[0, 1] 
    message: str