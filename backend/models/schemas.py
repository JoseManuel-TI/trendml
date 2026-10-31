from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    phone: Optional[str] = None
    subscription_plan: str

    class Config:
        from_attributes = True


class TrendingItem(BaseModel):
    product_id: str
    title: str
    growth_rate: float
    last_price: float
    sold_quantity: int
    captured_at: datetime


class PriceAlertItem(BaseModel):
    product_id: str
    title: str
    previous_price: float
    current_price: float
    diff_percentage: float
    captured_at: datetime


class PredictionItem(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    product_id: str
    title: str
    predicted_sales_next_week: Optional[float]
    status: str
    horizon_days: int
    model_version: str
    captured_at: datetime


class TopSellerItem(BaseModel):
    seller_id: str
    total_products: int
    avg_sales: float


class MLTokenResponse(BaseModel):
    is_connected: bool
    has_refresh_token: bool
    expires_at: Optional[datetime] = None
    user_id: int
