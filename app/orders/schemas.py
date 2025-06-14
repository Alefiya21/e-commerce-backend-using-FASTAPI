from pydantic import BaseModel
from app.orders.models import OrderStatus
from datetime import datetime
from typing import List

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price_at_purchase: float
    subtotal: float
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: OrderStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderDetailResponse(BaseModel):
    id: int
    total_amount: float
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True

class OrderHistoryResponse(BaseModel):
    orders: List[OrderResponse]
    total: int