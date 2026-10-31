from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    subscription_plan: Mapped[str] = mapped_column(String(50), default="starter")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ml_tokens: Mapped[list["MLToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    seller_id: Mapped[str] = mapped_column(String(50), index=True)
    category_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    permalink: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    history: Mapped[list["PriceHistory"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[str] = mapped_column(String(50), ForeignKey("products.id"), index=True)
    price: Mapped[float] = mapped_column(Float)
    sold_quantity: Mapped[int] = mapped_column(Integer)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    data_source: Mapped[str] = mapped_column(String(30), default="unknown", server_default="unknown")

    product: Mapped["Product"] = relationship(back_populates="history")


class TrendSnapshot(Base):
    __tablename__ = "trend_snapshots"
    __table_args__ = (UniqueConstraint("product_id", "captured_at", name="uq_trend_product_time"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[str] = mapped_column(String(50), ForeignKey("products.id"), index=True)
    growth_rate: Mapped[float] = mapped_column(Float)
    predicted_sales_next_week: Mapped[float] = mapped_column(Float, default=0.0)
    is_trending: Mapped[bool] = mapped_column(Boolean, default=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class CheckoutAttempt(Base):
    __tablename__ = "checkout_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    plan: Mapped[str] = mapped_column(String(20), index=True)
    provider: Mapped[str] = mapped_column(String(20), default="mercadopago")
    preference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    checkout_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class MLToken(Base):
    __tablename__ = "ml_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, index=True)
    access_token: Mapped[str] = mapped_column(Text)
    refresh_token: Mapped[str] = mapped_column(Text, default="")
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="ml_tokens")


class WeeklyPrediction(Base):
    __tablename__ = "weekly_predictions"
    __table_args__ = (UniqueConstraint("product_id", "captured_at", name="uq_weekly_product_time"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(String(50), ForeignKey("products.id"), index=True)
    predicted_increment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(30))
    model_version: Mapped[str] = mapped_column(String(50))
    captured_at: Mapped[datetime] = mapped_column(DateTime, index=True)
