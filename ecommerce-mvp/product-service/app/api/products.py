"""Product API endpoints"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from bson import ObjectId
from app.core.database import get_database
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
import sys
sys.path.append('/app')
from shared.auth import get_current_user, require_admin

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """List products with filters"""
    db = get_database()

    query = {"is_active": True}

    if category:
        query["category"] = category

    if search:
        query["$text"] = {"$search": search}

    if min_price is not None or max_price is not None:
        query["price"] = {}
        if min_price is not None:
            query["price"]["$gte"] = min_price
        if max_price is not None:
            query["price"]["$lte"] = max_price

    cursor = db.products.find(query).skip(skip).limit(limit)
    products = await cursor.to_list(length=limit)

    return [ProductResponse(**{**p, "_id": str(p["_id"])}) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get product by ID"""
    db = get_database()

    try:
        product = await db.products.find_one({"_id": ObjectId(product_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID")

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse(**{**product, "_id": str(product["_id"])})


@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    current_user: dict = Depends(require_admin)
):
    """Create new product (admin only)"""
    db = get_database()

    product_dict = product.model_dump()
    result = await db.products.insert_one(product_dict)

    created_product = await db.products.find_one({"_id": result.inserted_id})
    return ProductResponse(**{**created_product, "_id": str(created_product["_id"])})


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    current_user: dict = Depends(require_admin)
):
    """Update product (admin only)"""
    db = get_database()

    try:
        oid = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID")

    update_data = {k: v for k, v in product_update.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db.products.update_one(
        {"_id": oid},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    updated_product = await db.products.find_one({"_id": oid})
    return ProductResponse(**{**updated_product, "_id": str(updated_product["_id"])})


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    current_user: dict = Depends(require_admin)
):
    """Delete product (soft delete - admin only)"""
    db = get_database()

    try:
        oid = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID")

    result = await db.products.update_one(
        {"_id": oid},
        {"$set": {"is_active": False}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted successfully"}


@router.get("/categories/list")
async def list_categories():
    """List all product categories"""
    db = get_database()

    categories = await db.products.distinct("category", {"is_active": True})
    return {"categories": categories}
