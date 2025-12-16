# schemas/report.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    report_at: datetime
    order_id: str
    count_product: int
