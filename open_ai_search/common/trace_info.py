from logging import Logger
from typing import Optional

import shortuuid

from open_ai_search.common.logger import get_logger


class TraceInfo:
    def __init__(self, trace_id: Optional[str] = None, logger: Optional[Logger] = None, payload: Optional[dict] = None):
        self.trace_id = trace_id or shortuuid.uuid()
        self.logger = logger or get_logger()
        if self.trace_id not in self.logger.name.split("."):
            self.logger = self.logger.getChild(self.trace_id)
        self.payload: dict = payload or {}

    def get_child(self, name: str = None, addition_payload: Optional[dict] = None) -> "TraceInfo":
        return self.__class__(
            self.trace_id,
            self.logger if name is None else self.logger.getChild(name),
            self.payload | (addition_payload or {})
        )

    def info(self, payload: dict):
        self.logger.info(self.payload | payload)

    def warning(self, payload: dict):
        self.logger.warning(self.payload | payload)

    def exception(self, payload: dict):
        self.logger.exception(self.payload | payload)

    def __setitem__(self, key, value):
        self.payload = self.payload | {key: value}
