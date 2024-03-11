import asyncio
import os
import signal

from discord import Intents
from discord.ext import commands
from loguru import logger

from austastic.cogs.health import Health
from austastic.cogs.mesh import Mesh

TOKEN = os.getenv("DISCORD_TOKEN")
PING_URL = os.getenv("PING_URL")
PREFIXES = [os.getenv("DISCORD_PREFIX", "./")]


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super(Bot, self).__init__(**kwargs)

    async def on_ready(self):
        logger.info("{} has connected to Discord!", self.user)
        logger.complete()


intents = Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
intents.members = True

bot = Bot(
    command_prefix=PREFIXES,
    case_insensitive=True,
    description="Austin Mesh radio informational bot",
    intents=intents,
    owner_id=206914075391688704,
)


async def start_bot():
    if TOKEN:
        if PING_URL:
            await bot.add_cog(Health(bot, PING_URL))
        await bot.add_cog(Mesh(bot))
        await bot.start(TOKEN)
    else:
        logger.error("Please set your DISCORD_TOKEN.")
        await logger.complete()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    main_task = loop.create_task(start_bot())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, main_task.cancel)
    try:
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        logger.error("Received signal to terminate bot")
    finally:
        loop.stop()
