import random
import logging
import time

logger = logging.getLogger(__name__)

def process_payment(amount: float) -> dict:
    logger.info(f"Processing payment for amount: ${amount}")
    
    time.sleep(0.5) 
    
    success = random.random() < 0.95  # Simulate 95% success rate

    if success:
        logger.info("Payment successful")
        return {
            "success": True,
            "amount": amount,
            "message": "Payment processed successfully"
        }
    else:
        logger.warning("Payment failed - simulated failure")
        return {
            "success": False,
            "amount": amount,
            "message": "Payment processing failed"
        }