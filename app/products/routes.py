from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.products.models import Product
from app.products.schemas import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.middlewares.auth_middleware import get_admin_user
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Admin Product Routes
@router.post("/admin/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate,db: Session = Depends(get_db),admin_user = Depends(get_admin_user)):
    """Create a new product (Admin only)"""
    logger.info(f"Admin {admin_user.email} creating product: {product_data.name}")
    
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        category=product_data.category,
        image_url=product_data.image_url
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    logger.info(f"Product created successfully")
    return new_product

@router.get("/admin/products", response_model=ProductListResponse)
async def get_admin_products(db: Session = Depends(get_db),admin_user = Depends(get_admin_user)):
    """Get all products(Admin only)"""
    logger.info(f"Admin {admin_user.email} fetching all products")
    
    products = db.query(Product).all()
    total = db.query(Product).count()
    
    return ProductListResponse(
        products=products,
        total=total
    )

@router.get("/admin/products/{product_id}", response_model=ProductResponse)
async def get_admin_product(product_id: int,db: Session = Depends(get_db),admin_user = Depends(get_admin_user)):
    """Get product details (Admin only)"""
    logger.info(f"Admin {admin_user.email} fetching product: {product_id}")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": True, "message": "Product not found", "code": 404}
        )
    
    return product 

@router.put("/admin/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int,product_data: ProductUpdate,db: Session = Depends(get_db),admin_user = Depends(get_admin_user)):
    """Update product (Admin only)"""
    logger.info(f"Admin {admin_user.email} updating product: {product_id}")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": True, "message": "Product not found", "code": 404}
        )
    
    # Update only provided fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    logger.info(f"Product updated successfully: {product_id}")
    return product

@router.delete("/admin/products/{product_id}")
async def delete_product(product_id: int,db: Session = Depends(get_db),admin_user = Depends(get_admin_user)):
    """Delete product (Admin only)"""
    logger.info(f"Admin {admin_user.email} deleting product: {product_id}")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": True, "message": "Product not found", "code": 404}
        )
    
    db.delete(product)
    db.commit()
    
    logger.info(f"Product deleted successfully: {product_id}")
    return {"message": "Product deleted successfully"}

# User Product Routes
@router.get("/products", response_model=ProductListResponse)
async def get_products(category: Optional[str] = Query(None),
                       min_price: Optional[float] = Query(None, ge=0),max_price: Optional[float] = Query(None, ge=0),
                       sort_by: Optional[str] = Query("id", pattern="^(id|name|price)$"),db: Session = Depends(get_db)):
    """Get products with filters"""
    
    query = db.query(Product)
    
    # Apply filters
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if sort_by == "name":
        query = query.order_by(Product.name)
    elif sort_by == "price":
        query = query.order_by(Product.price)
    else:
        query = query.order_by(Product.id)
    
    products = query.all()
    total = query.count()
    
    return ProductListResponse(
        products=products,
        total=total
    )
@router.get("/products/search", response_model=ProductListResponse)
async def search_products(keyword: str = Query(..., min_length=1),db: Session = Depends(get_db)):
    """Search products by keyword"""
    logger.info(f"Product search - keyword: {keyword}")
    
    query = db.query(Product).filter(
        or_(
            Product.name.ilike(f"%{keyword}%"),
            Product.description.ilike(f"%{keyword}%"),
            Product.category.ilike(f"%{keyword}%")
        )
    )
    
    products = query.all()
    total = query.count()
    
    return ProductListResponse(
        products=products,
        total=total
    )

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product details"""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": True, "message": "Product not found", "code": 404}
        )
    
    return product