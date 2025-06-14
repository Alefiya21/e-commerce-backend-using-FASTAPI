from fastapi import FastAPI, Request
import logging
import time
from app.auth.routes import router as auth_router
from app.products.routes import router as products_router
from app.cart.routes import router as cart_router
from app.checkout.routes import router as checkout_router
from app.orders.routes import router as orders_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="E-commerce Backend",
    description="A robust e-commerce backend system",
    version="1.0.0"
) 

# Middleware for logging requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    client_ip = request.client.host
    method = request.method
    url = str(request.url)
    
    logger.info(f"Request: {method} {url} from {client_ip}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    return response

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(products_router, prefix="", tags=["Products"])
app.include_router(cart_router, prefix="/cart", tags=["Cart"])
app.include_router(checkout_router, prefix="/checkout", tags=["Checkout"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "E-commerce Backend API is running!"}