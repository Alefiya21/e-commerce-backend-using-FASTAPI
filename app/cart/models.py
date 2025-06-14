from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.core.database import Base

class Cart(Base):
    __tablename__ = "cart"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)