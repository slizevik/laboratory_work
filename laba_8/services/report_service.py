# services/report_service.py
from datetime import date
from typing import List
from repositories.report_repository import ReportRepository
from models import Report


class ReportService:
    def __init__(self, report_repository: ReportRepository):
        self.report_repository = report_repository

    async def get_by_date(self, report_date: date) -> List[Report]:
        """Получить все отчёты за указанную дату."""
        return await self.report_repository.get_by_date(report_date)
