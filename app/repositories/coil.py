from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select

from app.domain.models import Coil
from app.schemas.coil import CoilFilter


class CoilRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, length: float, weight: float) -> Coil:
        coil = Coil(length=length, weight=weight)
        self.session.add(coil)
        self.session.commit()
        self.session.refresh(coil)
        return coil

    def get_by_id(self, coil_id: int) -> Optional[Coil]:
        result = self.session.execute(
            select(Coil).where(Coil.id == coil_id)
        ).scalar_one_or_none()  # type: Optional[Coil]
        return result

    def remove(self, coil: Coil) -> Coil:
        coil.removed_at = datetime.now(timezone.utc)
        self.session.commit()
        self.session.refresh(coil)
        return coil

    def _apply_filters(self, query: Select, filters: CoilFilter) -> Select:
        if filters.id_range:
            query = query.where(
                Coil.id.between(filters.id_range[0], filters.id_range[1])
            )
        if filters.weight_range:
            query = query.where(
                Coil.weight.between(
                    filters.weight_range[0], filters.weight_range[1]
                )
            )
        if filters.length_range:
            query = query.where(
                Coil.length.between(
                    filters.length_range[0], filters.length_range[1]
                )
            )
        if filters.added_at_range:
            query = query.where(
                Coil.added_at.between(
                    filters.added_at_range[0], filters.added_at_range[1]
                )
            )
        if filters.removed_at_range:
            query = query.where(
                Coil.removed_at.between(
                    filters.removed_at_range[0], filters.removed_at_range[1]
                )
            )
        return query

    def get_all(self, filters: Optional[CoilFilter] = None) -> List[Coil]:
        query = select(Coil)
        if filters:
            query = self._apply_filters(query, filters)
        result = self.session.execute(query)
        return list(result.scalars().all())

    def get_statistics(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        # Получаем все рулоны в указанный период
        removed_or_null = or_(
            Coil.removed_at >= start_date, Coil.removed_at.is_(None)
        )
        condition = and_(Coil.added_at <= end_date, removed_or_null)

        coils_in_period = (
            self.session.execute(select(Coil).where(condition)).scalars().all()
        )

        # Если нет рулонов, возвращаем пустую статистику
        if not coils_in_period:
            return {
                "added_count": 0,
                "removed_count": 0,
                "avg_length": 0,
                "avg_weight": 0,
                "min_length": 0,
                "max_length": 0,
                "min_weight": 0,
                "max_weight": 0,
                "total_weight": 0,
                "min_storage_time": None,
                "max_storage_time": None,
            }

        # Подсчет добавленных рулонов
        added_count = self.session.scalar(
            select(func.count()).where(
                Coil.added_at.between(start_date, end_date)
            )
        )

        # Подсчет удаленных рулонов
        removed_count = self.session.scalar(
            select(func.count()).where(
                Coil.removed_at.between(start_date, end_date)
            )
        )

        # Рассчитываем статистику
        lengths = [coil.length for coil in coils_in_period]
        weights = [coil.weight for coil in coils_in_period]

        avg_length = sum(lengths) / len(lengths) if lengths else 0
        avg_weight = sum(weights) / len(weights) if weights else 0
        min_length = min(lengths) if lengths else 0
        max_length = max(lengths) if lengths else 0
        min_weight = min(weights) if weights else 0
        max_weight = max(weights) if weights else 0
        total_weight = sum(weights) if weights else 0

        # Максимальный и минимальный промежуток между добавлением и удалением
        coils_with_removal = [
            coil for coil in coils_in_period if coil.removed_at is not None
        ]

        min_diff = None
        max_diff = None

        if coils_with_removal:
            diffs = [
                (coil.removed_at - coil.added_at).total_seconds()
                for coil in coils_with_removal
            ]
            if diffs:
                min_diff = str(min(diffs)) if diffs else None
                max_diff = str(max(diffs)) if diffs else None

        return {
            "added_count": added_count or 0,
            "removed_count": removed_count or 0,
            "avg_length": avg_length,
            "avg_weight": avg_weight,
            "min_length": min_length,
            "max_length": max_length,
            "min_weight": min_weight,
            "max_weight": max_weight,
            "total_weight": total_weight,
            "min_storage_time": min_diff,
            "max_storage_time": max_diff,
        }
