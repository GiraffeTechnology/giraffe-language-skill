"""Trade RFQ schema definition and constants."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

SCHEMA_VERSION = "trade_rfq.v1"

# Critical fields. Tuples denote "at least one of" alternatives.
CRITICAL_FIELDS: tuple[object, ...] = (
    "quantity",
    ("product_name", "product_category"),
    "destination",
    ("lead_time_days", "delivery_deadline"),
)


class TradeRFQFields(BaseModel):
    """Structured trade RFQ. Nullable fields default to ``None``."""

    quantity: int | None = None
    quantity_unit: str | None = "pcs"
    product_name: str | None = None
    product_category: str | None = None
    product_modifier: list[str] = Field(default_factory=list)
    destination: str | None = None
    lead_time_days: int | None = None
    delivery_deadline: str | None = None
    quality_level: str | None = None
    intent: str | None = None

    def to_ordered_dict(self) -> dict[str, Any]:
        return {
            "quantity": self.quantity,
            "quantity_unit": self.quantity_unit,
            "product_name": self.product_name,
            "product_category": self.product_category,
            "product_modifier": self.product_modifier,
            "destination": self.destination,
            "lead_time_days": self.lead_time_days,
            "quality_level": self.quality_level,
            "intent": self.intent,
        }
