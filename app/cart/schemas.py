from pydantic import BaseModel, field_validator
from fastapi import HTTPException, status

class CartAdd(BaseModel):
    product_id: int
    quantity: int = 1
    
    @field_validator('quantity')
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": True, "message": "Quantity must be greater than 0", "code": 400}
            )
        return v

class CartUpdate(BaseModel):
    quantity: int
    
    @field_validator('quantity')
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": True, "message": "Quantity must be greater than 0", "code": 400}
            )
        return v

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    quantity: int
    subtotal: float
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_items: int
    total_amount: float