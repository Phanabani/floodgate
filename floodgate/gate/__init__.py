from floodgate.floodgate import Floodgate
from .cog import Gate


def setup(bot: Floodgate):
    bot.add_cog(Gate(bot, config=bot.modules_config.floodgate))
