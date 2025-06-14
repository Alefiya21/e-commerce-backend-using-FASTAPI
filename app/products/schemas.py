from pydantic import BaseModel, field_validator
from typing import Optional
from fastapi import HTTPException, status

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": True, "message": "Product name cannot be empty", "code": 400}
            )
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        if not v.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": True, "message": "Category cannot be empty", "code": 400}
            )
        return v

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": True, "message": "Price must be greater than 0", "code": 400}
            )
        return v
    
    @field_validator('stock')
    @classmethod
    def stock_must_be_positive(cls, v):
        if v < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": True, "message": "Stock must be non-negative", "code": 400}
            )
        return v

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    
    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": True, "message": "Price must be greater than 0", "code": 400}
            )
        return v
    
    @field_validator('stock')
    @classmethod
    def stock_must_be_positive(cls, v):
        if v < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": True, "message": "Stock must be non-negative", "code": 400}
            )
        return v

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: str
    image_url: Optional[str]
    
    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int