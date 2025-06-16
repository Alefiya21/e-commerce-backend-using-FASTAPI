from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.orders.models import Order, OrderItem
from app.orders.schemas import OrderResponse, OrderDetailResponse, OrderHistoryResponse, OrderItemResponse
from app.products.models import Product
from app.middlewares.auth_middleware import get_current_user
from app.auth.models import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", response_model=OrderHistoryResponse)
async def get_order_history(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """Get user's order history"""
    logger.info(f"User {current_user.email} fetching order history")
    
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(Order.created_at.desc()).all()

    if not orders:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": True, "message": "No orders found", "code": 404}
        )
    
    return OrderHistoryResponse(
        orders=[OrderResponse.model_validate(order) for order in orders],
        total=len(orders)
    )

@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order_details(order_id: int,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """Get order details"""
    logger.info(f"User {current_user.email} fetching order details: {order_id}")
    
    # Find order
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": True, "message": "Order not found", "code": 404}
        )
    
    # Get order items with product details
    order_items = db.query(OrderItem, Product).join(
        Product, OrderItem.product_id == Product.id,isouter= True,
    ).filter(OrderItem.order_id == order_id).all()
    
    items = []
    for order_item, product in order_items:
        name = product.name if product else "the product is no longer available"
        product_id = product.id   if product else order_item.product_id
        subtotal = order_item.price_at_purchase * order_item.quantity
        items.append(OrderItemResponse(
            id=order_item.id,
            product_id=product_id,
            product_name=name,
            quantity=order_item.quantity,
            price_at_purchase=order_item.price_at_purchase,
            subtotal=subtotal
        ))
    
    return OrderDetailResponse(
        id=order.id,
        total_amount=order.total_amount,
        status=order.status,
        created_at=order.created_at,
        items=items
    )