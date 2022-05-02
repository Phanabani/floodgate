import asyncio
from collections.abc import Coroutine
import datetime as dt
import logging
from typing import Optional

import discord
from discord.ext import commands, tasks
import pendulum as pen

from floodgate.common.time import random_time
from floodgate.config import Config

__all__ = ["Gate"]

logger = logging.getLogger("floodgate.gate")
# noinspection PyProtectedMember
FloodgateConfig = Config._Bot._Modules._Floodgate
# noinspection PyProtectedMember
ChannelConfig = FloodgateConfig._Channel


def _handle_task_exception(task: asyncio.Task) -> None:
    try:
        task.result()
    except asyncio.CancelledError:
        pass  # Task cancellation should not be logged as an error.
    except Exception as e:
        logger.error(f"Exception raised by task {task}", exc_info=e)


class GateController:
    _open_gate_task: Optional[asyncio.Task] = None
    _close_gate_task: Optional[asyncio.Task] = None

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        channel: discord.TextChannel,
        config: ChannelConfig,
    ):
        self._loop = loop
        self._channel = channel
        self._config = config

        self._closed = True

        self._schedule_tasks()

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def scheduled(self):
        return self._open_gate_task is not None

    def _schedule_tasks(self):
        open_delay, close_delay = self._get_delay_times()
        if open_delay < 0:
            return
        self._open_gate_task = self._create_task(self._on_open(open_delay))
        self._close_gate_task = self._create_task(self._on_close(close_delay))

    def _get_delay_times(self) -> tuple[float, float]:
        config = self._config.gate_open
        now = pen.now()
        today = pen.today(config.timezone)

        if config.time is not None:
            # Scheduled time
            time = config.time
        else:
            # Random time
            time = random_time(config.time_window_start, config.time_window_end)

        start_dt = pen.instance(dt.datetime.combine(today, time), tz=config.timezone)
        start_delay = (start_dt - now).total_seconds()
        end_delay = start_delay + config.duration.total_seconds()
        return start_delay, end_delay

    def _create_task(self, coro: Coroutine[None]) -> Optional[asyncio.Task]:
        task = self._loop.create_task(coro)
        task.add_done_callback(_handle_task_exception)
        return task

    async def _on_open(self, sleep_time: float):
        await asyncio.sleep(sleep_time)
        self._closed = False
        await self._try_send_message(self._config.messages.open)

    async def _on_close(self, sleep_time: float):
        await asyncio.sleep(sleep_time)
        self._closed = True
        await self._try_send_message(self._config.messages.close)

    async def _try_send_message(self, msg: str):
        try:
            await self._channel.send(msg)
        except Exception as e:
            logger.error(
                f"Failed to send gate open message (channel_id={self._channel.id})",
                exc_info=e,
            )

    def cancel(self):
        if self._open_gate_task is not None:
            self._open_gate_task.cancel()
            self._open_gate_task = None
        if self._close_gate_task is not None:
            self._close_gate_task.cancel()
            self._close_gate_task = None


class Gate(commands.Cog):
    def __init__(self, bot: commands.Bot, config: FloodgateConfig):
        self._bot = bot
        self._gates: dict[int, GateController] = {}
        self._config = None
        self.set_config(config)

    def set_config(self, config: FloodgateConfig):
        self._config = config
        asyncio.run_coroutine_threadsafe(self._init_daily_loop(), self._bot.loop)

    async def _init_daily_loop(self):
        await self._bot.wait_until_ready()
        self._daily_loop.stop()
        self._daily_loop.start()

    @tasks.loop(hours=24)
    async def _daily_loop(self):
        await self._schedule_todays_gate_openings()

    @_daily_loop.error
    async def _on_daily_loop_error(self, exc: Exception):
        logger.error("Unhandled exception in daily_loop task", exc_info=exc)

    async def _schedule_todays_gate_openings(self):
        if self._config is None:
            raise RuntimeError("No config has been set")

        scheduled_count = 0
        for channel_id, channel_config in self._config.channels.items():
            channel = self._bot.get_channel(channel_id)
            if channel is None:
                logger.warning(f"Channel with ID {channel_id} cannot be found")
                continue
            self._gates[channel_id] = task = GateController(
                self._bot.loop, channel, channel_config
            )
            if task.scheduled:
                scheduled_count += 1
        logger.info(f"{scheduled_count} gate openings scheduled for today")

    async def _try_delete_gate(self, channel_id: int):
        if channel_id not in self._gates:
            return
        logger.info(f"Canceling gate opening (channel_id={channel_id})")
        self._gates[channel_id].cancel()
        del self._gates[channel_id]

    @commands.Cog.listener(name="on_message")
    async def leak_prevention(self, msg: discord.Message):
        """Delete new messages in channels with closed floodgates"""
        if msg.author.id == self._bot.user.id:
            return

        try:
            gate = self._gates[msg.channel.id]
        except KeyError:
            return

        if not gate.closed:
            return

        try:
            await msg.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException) as e:
            logger.error(
                f"Failed to delete message in channel with a closed floodgate "
                f"(message_id={msg.id}, channel={msg.channel.name}, "
                f"guild={msg.guild.name})",
                exc_info=e,
            )

    @commands.command()
    async def ping(self, context: commands.Context):
        await context.reply("Pong!")
