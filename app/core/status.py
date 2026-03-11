# app/core/status.py
from enum import Enum


class RequestStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    finished = "finished"
    failed = "failed"
