from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from db.connection import async_session
from db.models import Report
from db.repositories.base import BaseRepository


class ReportRepository(BaseRepository):
    model = Report

    @classmethod
    async def get_paginated(cls, page: int, per_page: int = 5, **filters):
        async with async_session() as session:

            base_query = (
                select(cls.model)
                .filter_by(**filters)
                .where(cls.model.is_finished.is_(True))
            )

            count_query = select(func.count()).select_from(base_query.subquery())
            total = await session.scalar(count_query)

            query = (
                base_query.options(
                    selectinload(cls.model.user),
                    selectinload(cls.model.tool),
                    selectinload(cls.model.vehicle),
                )
                .order_by(cls.model.id.desc())
                .limit(per_page)
                .offset((page - 1) * per_page)
            )

            result = await session.execute(query)
            items = result.scalars().all()

            return items, total

    @classmethod
    async def get_with_relations(cls, report_id: int):
        async with async_session() as session:
            query = (
                select(cls.model)
                .options(
                    selectinload(cls.model.media),
                    selectinload(cls.model.user),
                    selectinload(cls.model.tool),
                    selectinload(cls.model.vehicle),
                )
                .where(cls.model.id == report_id)
            )

            result = await session.execute(query)
            return result.scalar_one_or_none()
