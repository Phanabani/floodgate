import logging
from pathlib import Path
import sys

import discord
import discord.ext.commands as commands
import yaml
from yaml import Loader as YamlLoader

from floodgate.config import Config

__all__ = ["Floodgate", "run_bot"]

logger = logging.getLogger("floodgate")


# noinspection PyMethodMayBeStatic
class Floodgate(commands.Bot):
    def __init__(self, config: Config._Bot):

        intents = discord.Intents(guilds=True)
        allowed_mentions = discord.AllowedMentions(users=True)
        activity = discord.Game(f"{config.command_prefix}help")

        super().__init__(
            # Client params
            max_messages=None,
            intents=intents,
            allowed_mentions=allowed_mentions,
            activity=activity,
            # Bot params
            command_prefix=config.command_prefix,
            description=config.description,
        )

        self.load_extension("floodgate.gate")

    async def on_connect(self):
        logger.info("Client connected")

    async def on_disconnect(self):
        logger.info("Client disconnected")

    async def on_resumed(self):
        logger.info("Session resumed")

    async def on_ready(self):
        logger.info("Client started")

    async def on_error(self, event_method: str, *args, **kwargs):
        exc_type, __, __ = sys.exc_info()

        if exc_type is discord.HTTPException:
            logger.warning("HTTP exception", exc_info=True)
        elif exc_type is discord.Forbidden:
            logger.warning("Forbidden request", exc_info=True)

        elif event_method == "on_message":
            msg: discord.Message = args[0]
            logger.error(
                f"Unhandled in on_message (content: {msg.content!r} "
                f"author: {msg.author} channel: {msg.channel})",
                exc_info=True,
            )
        else:
            logger.error(
                f"Unhandled in {event_method} (args: {args} kwargs: {kwargs})",
                exc_info=True,
            )


def run_bot():
    # Load config
    config_path = Path(__file__).parent / "config.yml"
    with config_path.open() as f:
        config = Config.parse_obj(yaml.load(f, YamlLoader))

    # Floodgate logging
    logger = logging.getLogger("floodgate")
    logger.setLevel(config.logging.floodgate_logging_level)
    logger.addHandler(config.logging.handler)

    # Discord logging
    logger = logging.getLogger("discord")
    logger.setLevel(config.logging.discord_logging_level)
    logger.addHandler(config.logging.handler)

    # Run bot
    floodgate = Floodgate(config.bot)
    floodgate.loop.set_debug(True)
    floodgate.run(config.bot_token.get_secret_value())
