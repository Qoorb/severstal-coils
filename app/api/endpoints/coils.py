from datetime import datetime, timezone
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.coil import CoilRepository
from app.schemas.coil import (
    CoilCreate,
    CoilDeleteResponse,
    CoilFilter,
    CoilResponse,
    CoilResponseWrapper,
    CoilUpdate,
    DateRange,
)

router = APIRouter()


@router.get("/healthchecker")
def healthcheck() -> Dict[str, str]:
    return {"message": "The API is LIVE!!"}


@router.post(
    "/coils/", response_model=CoilResponse, status_code=status.HTTP_201_CREATED
)
def create_coil(
    coil: CoilCreate, db: Session = Depends(get_db)
) -> CoilResponse:
    repo = CoilRepository(db)
    db_coil = repo.create(length=coil.length, weight=coil.weight)
    return CoilResponse.model_validate(db_coil)


@router.get("/coils/{coil_id}", response_model=CoilResponseWrapper)
def get_coil(
    coil_id: int, db: Session = Depends(get_db)
) -> CoilResponseWrapper:
    repo = CoilRepository(db)
    coil = repo.get_by_id(coil_id)
    if not coil:
        raise HTTPException(
            status_code=404, detail=f"Рулон с этим id: `{coil_id}` не найден"
        )
    return CoilResponseWrapper(Coil=CoilResponse.model_validate(coil))


@router.patch(
    "/coils/{coil_id}",
    response_model=CoilResponseWrapper,
    status_code=status.HTTP_202_ACCEPTED,
)
def update_coil(
    coil_id: int, coil: CoilUpdate, db: Session = Depends(get_db)
) -> CoilResponseWrapper:
    repo = CoilRepository(db)
    db_coil = repo.get_by_id(coil_id)
    if not db_coil:
        raise HTTPException(
            status_code=404, detail=f"Рулон с этим id: `{coil_id}` не найден"
        )

    if coil.length is not None:
        db_coil.length = coil.length
    if coil.weight is not None:
        db_coil.weight = coil.weight

    db_coil.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_coil)

    return CoilResponseWrapper(Coil=CoilResponse.model_validate(db_coil))


@router.delete(
    "/coils/{coil_id}",
    response_model=CoilDeleteResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def remove_coil(
    coil_id: int, db: Session = Depends(get_db)
) -> CoilDeleteResponse:
    repo = CoilRepository(db)
    coil = repo.get_by_id(coil_id)
    if not coil:
        raise HTTPException(
            status_code=404, detail=f"Рулон с этим id: `{coil_id}` не найден"
        )
    if coil.removed_at:
        raise HTTPException(status_code=400, detail="Рулон уже удален")
    repo.remove(coil)
    return CoilDeleteResponse()


@router.get("/coils/", response_model=List[CoilResponse])
def get_coils(
    id_min: Optional[int] = None,
    id_max: Optional[int] = None,
    weight_min: Optional[float] = None,
    weight_max: Optional[float] = None,
    length_min: Optional[float] = None,
    length_max: Optional[float] = None,
    added_after: Optional[datetime] = None,
    added_before: Optional[datetime] = None,
    removed_after: Optional[datetime] = None,
    removed_before: Optional[datetime] = None,
    db: Session = Depends(get_db),
) -> List[CoilResponse]:
    filters = CoilFilter(
        id_range=(id_min, id_max) if id_min and id_max else None,
        weight_range=(
            (weight_min, weight_max) if weight_min and weight_max else None
        ),
        length_range=(
            (length_min, length_max) if length_min and length_max else None
        ),
        added_at_range=(
            (added_after, added_before)
            if added_after and added_before
            else None
        ),
        removed_at_range=(
            (removed_after, removed_before)
            if removed_after and removed_before
            else None
        ),
    )

    repo = CoilRepository(db)
    coils = repo.get_all(filters)
    return [CoilResponse.model_validate(coil) for coil in coils]


@router.post("/coils/statistics/", response_model=dict)
def get_statistics(
    date_range: DateRange, db: Session = Depends(get_db)
) -> dict:
    if date_range.end_date < date_range.start_date:
        raise HTTPException(
            status_code=400,
            detail="Дата окончания должна быть позже даты начала",
        )

    repo = CoilRepository(db)
    return repo.get_statistics(date_range.start_date, date_range.end_date)
