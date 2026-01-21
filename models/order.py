from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, ConfigDict
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

# api - order / GET 的回傳格式
class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    number: str # 20210425121135(訂單編號)
    price: int
    trip: Trip
    contact: Contact
    status: Literal[0, 1] = Field(default=1, description="支付狀態: 0 為失敗, 1 為成功")

    # 把拼裝api回應格式的程式碼從api(router)層移出
    @classmethod
    def actualizer(cls, result:dict):
        if not result:
            return None
        
        attraction = BookingAttraction(
            id=result["attraction_id"],
            name=result["attraction_name"],
            address=result["attraction_address"],
            image=result["attraction_image"]
        )

        # 組裝 Trip (處理日期字串)
        trip = Trip(
            attraction=attraction,
            date=str(result["trip_date"]),
            time=result["trip_time"]
        )

        # 組裝 Contact (處理欄位名稱不一致: contact_name -> name)
        contact = Contact(
            name=result["contact_name"],
            email=result["contact_email"],
            phone=result["contact_phone"]
        )

        # 最後回傳組裝好的 Order
        return cls(
            number=result['number'],
            price=result['price'],
            trip=trip,
            contact=contact,
            status=result['status']
        )


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