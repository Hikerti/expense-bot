from enum import StrEnum


class TransactionStatus(StrEnum):
    OK = "ok"
    CREDITOR = "creditor"
    FORECAST = "forecast"