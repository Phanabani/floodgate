from __future__ import annotations

from functools import cached_property
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Annotated, Literal, Optional

import pendulum as pen
from pendulum.tz.timezone import Timezone
from pydantic import BaseModel, Field, SecretStr, conint

import floodgate
from floodgate.common.pydantic_helpers import *
from floodgate.common.time import *

__all__ = ["Config"]

root_path = Path(floodgate.__path__[0])
logging_levels = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class TimezoneField(Timezone, FieldConverter):
    @classmethod
    def _pyd_convert_str(cls, timezone_str: str):
        return cls(timezone_str)

    @classmethod
    def _pyd_convert_timezone(cls, timezone: Timezone):
        return cls(timezone.name)


class TimeField(pen.Time, FieldConverter):
    @classmethod
    def _pyd_convert(cls, time_str: str):
        return parse_time(time_str, class_=cls)


class DurationField(pen.Duration, FieldConverter):
    @classmethod
    def _pyd_convert(cls, duration_str: str):
        return parse_duration(duration_str, class_=cls)


class Config(BaseModel):
    version: int = 120

    bot_token: SecretStr

    class _Bot(BaseModel):
        command_prefix: str = "!floodgate "
        description: str = "A Discord bot that allows messages in channels for only a specified amount of time."

        class _Modules(BaseModel):
            class _Floodgate(BaseModel):
                class _Channel(BaseModel):
                    class _GateOpen(BaseModel):
                        timezone: TimezoneField
                        duration: DurationField

                        time: Optional[TimeField] = None
                        # OR
                        time_window_start: Optional[TimeField] = None
                        time_window_end: Optional[TimeField] = None

                        _check_one_of_times = only_one_of(
                            "time",
                            ["time_window_start", "time_window_end"],
                            need_all=[True, False],
                        )

                    class _Messages(BaseModel):
                        open: str
                        close: str

                    gate_open: _GateOpen = Factory(_GateOpen)
                    messages: _Messages = Factory(_Messages)

                channels: dict[int, _Channel] = Factory(dict)

            floodgate: _Floodgate = Factory(_Floodgate)

        modules: _Modules = Factory(_Modules)

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

        _norm_output_file = maybe_relative_path("output_file", root_path)

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


update_forward_refs_recursive(Config)
