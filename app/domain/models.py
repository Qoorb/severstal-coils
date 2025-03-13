from datetime import UTC, datetime
from typing import Any, Dict

from sqlalchemy import DateTime, Float, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Coil(Base):
    __tablename__ = "coils"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    length: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    added_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    removed_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "length": self.length,
            "weight": self.weight,
            "added_at": self.added_at,
            "removed_at": self.removed_at,
            "updated_at": self.updated_at,
        }
