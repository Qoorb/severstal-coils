from datetime import datetime
from typing import Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field


class CoilBase(BaseModel):
    length: float = Field(
        ..., gt=0, description="Length of the coil in meters"
    )
    weight: float = Field(
        ..., gt=0, description="Weight of the coil in kilograms"
    )


class CoilCreate(CoilBase):
    pass


class CoilUpdate(BaseModel):
    length: Optional[float] = Field(None, gt=0)
    weight: Optional[float] = Field(None, gt=0)


class CoilInDB(CoilBase):
    id: int
    added_at: datetime
    removed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CoilResponse(CoilInDB):
    pass


class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime


class CoilFilter(BaseModel):
    id_range: Optional[Tuple[int, int]] = None
    weight_range: Optional[Tuple[float, float]] = None
    length_range: Optional[Tuple[float, float]] = None
    added_at_range: Optional[Tuple[datetime, datetime]] = None
    removed_at_range: Optional[Tuple[datetime, datetime]] = None


class APIResponse(BaseModel):
    """Base API response format"""

    Status: str = "Success"


class CoilResponseWrapper(APIResponse):
    """Wrapper for single coil response"""

    Coil: CoilResponse


class CoilDeleteResponse(APIResponse):
    """Response format for delete operation"""

    Message: str = "Coil deleted successfully"
