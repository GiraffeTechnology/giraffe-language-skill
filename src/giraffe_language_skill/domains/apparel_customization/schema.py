"""Apparel customization schema definition and constants."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

SCHEMA_VERSION = "apparel_customization.v1"

CRITICAL_FIELDS: tuple[object, ...] = (
    "garment_type",
    "quantity",
    "delivery_destination",
)


class ApparelCustomizationFields(BaseModel):
    garment_type: str | None = None
    fabric: str | None = None
    color: str | None = None
    gender: str | None = None
    quantity: int | None = None
    delivery_destination: str | None = None
    delivery_deadline: str | None = None
    customization_notes: list[str] = Field(default_factory=list)

    def to_ordered_dict(self) -> dict[str, Any]:
        return {
            "garment_type": self.garment_type,
            "fabric": self.fabric,
            "color": self.color,
            "gender": self.gender,
            "quantity": self.quantity,
            "delivery_destination": self.delivery_destination,
            "delivery_deadline": self.delivery_deadline,
            "customization_notes": self.customization_notes,
        }
