"""
MIT License

Copyright (c) 2024 dhrvd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import time
from contextlib import suppress
from logging import getLogger
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from moyai import Bot

log = getLogger(__name__)

INTERNAL_ERROR = "Something went wrong, Try again later."


class Meta(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        bot.on_error = self.on_error

        self.bot = bot

    async def on_error(self, event: str, *args, **kwargs) -> None:  # noqa: ANN002,ANN003
        log.exception("Unhandled exception in %s handler.", event)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        message = self.get_message(ctx, error)
        is_messageable = ctx.channel.permissions_for(ctx.guild.me).send_messages if ctx.guild is not None else True

        if message and is_messageable is None:
            with suppress(discord.HTTPException):
                await ctx.reply(message)

    def get_message(self, ctx: commands.Context, error: commands.CommandError) -> str | None:
        if isinstance(error, (commands.CheckFailure, commands.CommandNotFound, commands.DisabledCommand, commands.NotOwner)):
            return None

        log.exception("Unhandled command error.", exc_info=error)
        return INTERNAL_ERROR

    @commands.command(aliases=["latency", "rtt"])
    async def ping(self, ctx: commands.Context) -> None:
        """Measures the latency and response time of the bot."""
        content = f"The API latency is `{self.bot.latency * 1000:.0f}ms`"

        start = time.perf_counter()

        message = await ctx.reply(content)

        elapsed = time.perf_counter() - start
        content += f", and the round-trip time is `{elapsed * 1000:.0f}ms`."

        await message.edit(content=content)

    @commands.command()
    async def uptime(self, ctx: commands.Context) -> None:
        """Check how long the bot has been online for."""
        if self.bot.launched_at is None:
            await ctx.reply("N/A, Please try again in a few seconds.", ephemeral=True)
            return

        elapsed = discord.utils.utcnow() - self.bot.launched_at
        components = (("day", elapsed.days), ("hour", elapsed.seconds // 3600), ("minute", (elapsed.seconds % 3600) // 60))
        formatted = " ".join(f"{value} {unit}{'s' * (value > 1)}" for unit, value in components if value > 0)

        await ctx.reply(f"I have been online for {formatted}.")
