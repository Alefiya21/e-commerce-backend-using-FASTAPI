from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.cart.models import Cart
from app.products.models import Product
from app.orders.models import Order, OrderItem, OrderStatus
from app.middlewares.auth_middleware import get_current_user
from app.auth.models import User
from app.checkout.utils import process_payment
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("")
async def checkout(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """Checkout and place order"""
    
    # Get cart items
    cart_items = db.query(Cart, Product).join(
        Product, Cart.product_id == Product.id
    ).filter(Cart.user_id == current_user.id).all()
    
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": True, "message": "Cart is empty", "code": 400}
        )
    
    # Calculate total and validate stock
    total_amount = 0
    order_items_data = []
    
    for cart_item, product in cart_items:
        # Check stock availability
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": True, "message": f"Insufficient stock for {product.name}", "code": 400}
            )
        
        subtotal = product.price * cart_item.quantity
        total_amount += subtotal
        
        order_items_data.append({
            "product_id": product.id,
            "quantity": cart_item.quantity,
            "price_at_purchase": product.price,
            "product": product
        })
    
    # Process payment
    payment_result = process_payment(total_amount)
    
    if not payment_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": True, "message": "Payment failed", "code": 400}
        )
    
    try:
        # Create order
        new_order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            status=OrderStatus.PAID
        )
        db.add(new_order)
        db.flush()  # Ensure order ID is generated
        
        # Create order items and update stock
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                price_at_purchase=item_data["price_at_purchase"]
            )
            db.add(order_item)
            
            # Update product stock
            product = item_data["product"]
            product.stock -= item_data["quantity"]
        
        # Clear cart
        db.query(Cart).filter(Cart.user_id == current_user.id).delete()
        
        db.commit()
        
        logger.info(f"Checkout successful - Order ID: {new_order.id}, Total: ${total_amount}")
        
        return {
            "message": "Checkout successful",
            "order_id": new_order.id,
            "total_amount": total_amount,
            "status": "paid"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Checkout failed for user {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": "Checkout failed", "code": 500}
        )
