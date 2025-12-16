# controllers/report_controller.py
from datetime import date, datetime
from litestar import Controller, get
from litestar.di import Provide
from litestar.params import Parameter
from litestar.exceptions import ValidationException
from schemas.report import ReportResponse
from services.report_service import ReportService


class ReportController(Controller):
    path = "/report"

    @get()
    async def get_reports_by_date(
        self,
        report_service: ReportService,
        date: str = Parameter(
            description="Дата в формате YYYY-MM-DD (например, 2025-12-16)"
        ),
    ) -> dict:
        """Получить отчёты по заказам за указанную дату."""
        try:
            # Парсим строку даты в объект date
            report_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationException(
                detail=f"Неверный формат даты: {date}. Ожидается формат YYYY-MM-DD"
            )

        reports = await report_service.get_by_date(report_date)
        return {
            "date": date,
            "reports": [ReportResponse.model_validate(r) for r in reports],
            "total_count": len(reports),
        }
