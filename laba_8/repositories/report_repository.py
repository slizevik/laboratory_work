# repositories/report_repository.py
from datetime import date, datetime
from sqlalchemy import select, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from models import Report


class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_date(self, report_date: date) -> List[Report]:
        """Получить все отчёты за указанную дату.

        Сравниваем DATE(report_at) с переданной датой.
        """
        result = await self.session.execute(
            select(Report).where(
                cast(Report.report_at, Date) == report_date
            ).order_by(Report.report_at.desc())
        )
        return result.scalars().all()
