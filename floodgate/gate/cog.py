import logging

import discord
from discord.ext import commands

__all__ = [
    'Gate'
]

logger = logging.getLogger('floodgate.my_extension')


class Gate(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, context: commands.Context):
        await context.reply('Pong!')
