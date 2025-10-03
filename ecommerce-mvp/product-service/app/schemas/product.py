"""Product schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float = Field(..., gt=0)
    category: str
    stock: int = Field(..., ge=0)
    images: Optional[List[str]] = []
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: str
    price: float
    category: str
    stock: int
    images: List[str]
    is_active: bool

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Sample Product",
                "description": "This is a sample product",
                "price": 99.99,
                "category": "Electronics",
                "stock": 50,
                "images": ["product.jpg"],
                "is_active": True
            }
        }
