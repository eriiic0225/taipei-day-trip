from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date

# 建立 booking 的 class定義及欄位驗證
class BookingData(BaseModel):
    attractionId: int
    date: str
    time: str
    price: int

    @field_validator('date')
    @classmethod
    def check_date_not_passed(cls, value:str):
        if date.fromisoformat(value) < date.today():
            raise ValueError("預訂日期不可早於今天")
        return value

# api - booking / GET 的回傳格式
class BookingAttraction(BaseModel):
    # 開啟 from_attributes，允許pydantic從非 dict 的屬性讀取資料
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    image: str


class Booking(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attraction: BookingAttraction
    date: date
    time: str
    price: int

    @classmethod
    def create_from_db(cls, result:str):
        """
        工廠方法：將資料庫的扁平 dict 轉換為嵌套的 Booking 物件
        """
        if not result:
            return None
        
        # 映射（Mapping）邏輯
        # 利用 cls(...) 來實例化自己
        return cls(
            attraction=BookingAttraction.model_validate(result),
            date=result["date"],
            time=result["time"],
            price=result["price"]
        )