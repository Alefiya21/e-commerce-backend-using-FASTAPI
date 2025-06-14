from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.cart.models import Cart
from app.cart.schemas import CartAdd, CartUpdate, CartItemResponse, CartResponse
from app.products.models import Product
from app.middlewares.auth_middleware import get_current_user
from app.auth.models import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
async def add_to_cart(cart_data: CartAdd,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """Add item to cart"""
    logger.info(f"User {current_user.email} adding to cart - product: {cart_data.product_id}")
    
    # Check if product exists
    product = db.query(Product).filter(Product.id == cart_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": True, "message": "Product not found", "code": 404}
        )
    
    # Check stock availability
    if product.stock < cart_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": True, "message": "Insufficient stock", "code": 400}
        )
    
    # Check if item already in cart
    existing_cart_item = db.query(Cart).filter(
        Cart.user_id == current_user.id,
        Cart.product_id == cart_data.product_id
    ).first()
    
    if existing_cart_item:
        # Update quantity
        new_quantity = existing_cart_item.quantity + cart_data.quantity
        if product.stock < new_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": True, "message": "Insufficient stock.", "code": 400}
            )
        existing_cart_item.quantity = new_quantity
        db.commit()
        logger.info(f"Cart item updated - new quantity: {new_quantity}")
    else:
        # Add new item
        new_cart_item = Cart(
            user_id=current_user.id,
            product_id=cart_data.product_id,
            quantity=cart_data.quantity
        )
        db.add(new_cart_item)
        db.commit()
        logger.info(f"New item added to cart")
    
    return {"message": "Item added to cart successfully"}

@router.get("", response_model=CartResponse)
async def get_cart(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """Get user's cart"""
    logger.info(f"User {current_user.email} fetching cart items")
    
    cart_items = db.query(Cart, Product).join(
        Product, Cart.product_id == Product.id
    ).filter(Cart.user_id == current_user.id).all()
    
    items = []
    total_amount = 0
    total_items = 0
    
    for cart_item, product in cart_items:
        subtotal = product.price * cart_item.quantity
        total_amount += subtotal
        total_items += cart_item.quantity
        
        items.append(CartItemResponse(
            id=cart_item.id,
            product_id=product.id,
            product_name=product.name,
            product_price=product.price,
            quantity=cart_item.quantity,
            subtotal=subtotal,
        ))
    
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": True, "message": "Cart is empty", "code": 404}
        )
    
    return CartResponse(
        items=items,
        total_items=total_items,
        total_amount=total_amount
    )

@router.put("/{product_id}")
async def update_cart_quantity(product_id: int,cart_data: CartUpdate,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """Update cart item quantity"""
    logger.info(f"User {current_user.email} updating cart item: {product_id}")
    
    # Find cart item  
    cart_item = db.query(Cart).filter(
        Cart.user_id == current_user.id,
        Cart.product_id == product_id
    ).first() 
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": True, "message": "Cart item not found", "code": 404}
        )
    
    # Check product stock
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": True, "message": "Product not found", "code": 404}
        )
    
    # Check stock availability
    if product.stock < cart_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": True, "message": "Insufficient stock", "code": 400}
        )
    
    # Update quantity
    cart_item.quantity = cart_data.quantity
    db.commit()

    logger.info(f"Cart item quantity updated to: {cart_data.quantity}")
    return {"message": "Cart item updated successfully"}

@router.delete("/{product_id}")
async def remove_from_cart(product_id: int,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """Remove item from cart"""
    logger.info(f"User {current_user.email} removing item from cart: {product_id}")
    
    # Check cart item
    cart_item = db.query(Cart).filter(
        Cart.user_id == current_user.id,
        Cart.product_id == product_id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": True, "message": "Cart item not found", "code": 404}
        )
    
    db.delete(cart_item)
    db.commit()
    
    logger.info(f"Cart item removed successfully")
    return {"message": "Cart item removed successfully"}
