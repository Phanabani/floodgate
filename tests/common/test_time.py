import datetime as dt
import math
import statistics
from typing import Literal

from hypothesis import given
import hypothesis.strategies as st
import pendulum as pen
import pytest

from floodgate.common.time import *

UNIFORM_DISTRIBUTION_STDEV = math.sqrt(1 / 12)
DISTRIBUTION_TEST_COUNT = 10_000
DISTRIBUTION_TEST_STDEV_MAX = UNIFORM_DISTRIBUTION_STDEV + 0.01


@st.composite
def pen_time(
    draw,
    min_value: dt.time = dt.time.min,
    max_value: dt.time = dt.time.max,
    resolution: Literal["h", "m", "s", "us"] = "us",
):
    time: dt.time = draw(st.times(min_value, max_value))
    if resolution == "h":
        args = (time.hour,)
    elif resolution == "m":
        args = (time.hour, time.minute)
    elif resolution == "s":
        args = (time.hour, time.second)
    elif resolution == "us":
        args = (time.hour, time.microsecond)
    else:
        raise ValueError("resolution must be one of ['h', 'm', 's', 'us']")
    return pen.time(*args)


class TestRandomTime:
    @given(pen_time(resolution="s"), pen_time(resolution="s"))
    def test_end_less_than_start(self, start_time: pen.Time, end_time: pen.Time):
        if end_time < start_time:
            with pytest.raises(ValueError):
                random_time(start_time, end_time)

    @given(pen_time(resolution="s"), pen_time(resolution="s"))
    def test_same_hour(self, start_time: pen.Time, end_time: pen.Time):
        if end_time < start_time:
            return
        if start_time.hour != end_time.hour:
            return
        time = random_time(start_time, end_time)
        assert start_time <= time <= end_time

    @given(pen_time(resolution="s"), pen_time(resolution="s"))
    def test_same_hour_minute(self, start_time: pen.Time, end_time: pen.Time):
        if end_time < start_time:
            return
        if start_time.hour != end_time.hour:
            return
        if start_time.minute != end_time.minute:
            return
        time = random_time(start_time, end_time)
        assert start_time <= time <= end_time

    @given(pen_time(resolution="s"), pen_time(resolution="s"))
    def test_same_hour_minute_second(self, start_time: pen.Time, end_time: pen.Time):
        if end_time < start_time:
            return
        if start_time.hour != end_time.hour:
            return
        if start_time.minute != end_time.minute:
            return
        if start_time.second != end_time.second:
            return
        time = random_time(start_time, end_time)
        assert start_time <= time <= end_time

    @given(pen_time(resolution="s"), pen_time(resolution="s"))
    def test_even_distribution(self, start_time: pen.Time, end_time: pen.Time):
        if end_time < start_time:
            return
        total_seconds = (end_time - start_time).total_seconds()

        times = []
        for _ in range(DISTRIBUTION_TEST_COUNT):
            time = random_time(start_time, end_time)
            times.append((time - start_time).total_seconds())

        stdev_scaled = statistics.stdev(times) / total_seconds
        assert stdev_scaled <= DISTRIBUTION_TEST_STDEV_MAX
