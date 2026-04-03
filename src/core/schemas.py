from __future__ import annotations

from datetime import date as dt_date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.core.enums import TransactionStatus


class ParsedExpense(BaseModel):
    amount: Decimal | None = None
    currency: str | None = None
    description: str | None = None

    category_code: str | None = None
    account_code: str | None = None
    tranche_code: str | None = None

    counterparty: str | None = None
    date: dt_date | None = None
    is_recurring: bool | None = None
    status: TransactionStatus | None = None
    comment: str | None = None

    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class TransactionCreate(BaseModel):
    amount: Decimal
    currency: str
    description: str

    transaction_date: dt_date
    period: str

    counterparty: str | None = None
    is_recurring: bool
    status: TransactionStatus = TransactionStatus.OK
    comment: str | None = None

    fx_rate: Decimal
    amount_usd: Decimal

    category_id: int
    account_id: int
    tranche_id: int

    raw_input: str | None = None
    parse_confidence: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)


class ExportFilter(BaseModel):
    date_from: dt_date | None = None
    date_to: dt_date | None = None
    status: TransactionStatus | None = None
    tranche_id: int | None = None