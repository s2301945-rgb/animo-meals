from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Stall(Base):
    __tablename__ = 'stalls'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    location: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    menu_items: Mapped[list['MenuItem']] = relationship(back_populates='stall')


class MenuItem(Base):
    __tablename__ = 'menu_items'
    __table_args__ = (CheckConstraint('price >= 0', name='price_nonnegative'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    stall_id: Mapped[int] = mapped_column(ForeignKey('stalls.id'), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    category: Mapped[str] = mapped_column(String(30))
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
    stall: Mapped[Stall] = relationship(back_populates='menu_items')
