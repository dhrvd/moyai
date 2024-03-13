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

import datetime
import pathlib
from logging import getLogger

import discord
import jishaku  # noqa: F401
from discord.ext import commands

from moyai import config

log = getLogger(__name__)


class Bot(commands.Bot):
    launched_at: datetime.datetime | None = None

    def __init__(self) -> None:
        activity = discord.CustomActivity(name=config.STATUS)
        allowed_mentions = discord.AllowedMentions(everyone=False, users=False, roles=True, replied_user=False)
        intents = discord.Intents.all()

        super().__init__(
            command_prefix=commands.when_mentioned,
            help_command=None,
            case_insensitive=True,
            status=discord.Status.idle,
            activity=activity,
            allowed_mentions=allowed_mentions,
            intents=intents,
        )

    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")

        base = pathlib.Path("./moyai/plugins")
        plugins = [str(path.parent).replace("\\", ".") for path in base.glob("*/__init__.py")]

        for plugin in plugins:
            await self.load_extension(plugin)

    async def on_ready(self) -> None:
        prefix = "Reconnected"

        if not self.launched_at:
            self.launched_at = discord.utils.utcnow()
            prefix = "Logged in"

        if self.user:
            log.info("%s as %s#%s", prefix, self.user.name, self.user.discriminator)
