from __future__ import annotations

from functools import cached_property
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field, SecretStr, conint

import floodgate
from floodgate.common.pydantic_helpers import *

__all__ = ["Config"]

root_path = Path(floodgate.__path__[0])
logging_levels = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Config(BaseModel):
    version: int = 120

    bot_token: SecretStr

    class _Bot(BaseModel):
        command_prefix: str = "!floodgate "
        description: str = "A Discord bot that allows messages in channels for only a specified amount of time."

    bot: _Bot = Field(default_factory=_Bot)

    class _Logging(BaseModel):
        class Config:
            allow_mutation = False
            validate_all = True
            keep_untouched = (cached_property,)

        floodgate_logging_level: logging_levels = "INFO"
        discord_logging_level: logging_levels = "WARNING"
        output_file: Path = Path("./logs/floodgate.log")
        when: Literal["S", "M", "H", "D", "midnight"] = "midnight"
        interval: Annotated[int, conint(ge=1)] = 1
        backup_count: Annotated[int, conint(ge=0)] = 7
        format: str = "%(asctime)s %(levelname)s %(name)s | %(message)s"

        _normalize_output_file = validator_maybe_relative_path("output_file", root_path)

        @cached_property
        def formatter(self):
            return logging.Formatter(self.format)

        @cached_property
        def handler(self):
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            handler = TimedRotatingFileHandler(
                filename=self.output_file,
                when=self.when,
                interval=self.interval,
                backupCount=self.backup_count,
            )
            handler.setFormatter(self.formatter)
            return handler

    logging: _Logging = Field(default_factory=_Logging)


Config.update_forward_refs(**Config.__dict__)
