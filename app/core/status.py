# app/core/status.py
from enum import Enum


class RequestStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    FINISHED = "finished"
    FAILED = "failed"
