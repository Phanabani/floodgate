from discord.ext.commands import Bot

from .cog import Gate


def setup(bot: Bot):
    bot.add_cog(Gate(bot))
