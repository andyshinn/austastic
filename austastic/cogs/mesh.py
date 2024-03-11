from typing import Tuple, Union
from discord.ext import commands
from discord import Embed, User
from loguru import logger

from austastic.models import create_tables, Sighting, User, Node


def hex_or_id(node: Union[str, int]) -> Tuple[int, str]:
    if isinstance(node, str):
        node_id = int(node, 16)
    else:
        node_id = node

    return node_id, format(node_id, "x")


class Mesh(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Mesh cog initialized")


    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.bot.user} has connected to Discord!")
        await logger.complete()

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        logger.error(f"Error in event {event}: {args} {kwargs}")
        await logger.complete()

    @commands.command(name="sighting")
    async def sighting(self, ctx: commands.Context, node: hex_or_id):
        logger.debug(f"Sighting command received for node: {node} by {ctx.author}")

        try:
            user, created_user = User.get_or_create(discord_id=ctx.author.id)
            node, created_node = Node.get_or_create(id=node[0], hex=node[1])
            sighting: Sighting = Sighting.create(user=user, node=node)

            await ctx.send(
                f"Node **{node.id}** sighted by {ctx.author.display_name}. Node has been sighted **{node.sightings.count()}** times."
            )
        except Exception as e:
            logger.exception(e)
            await ctx.send(f"Error sighting node: {e}")
        finally:
            await logger.complete()

    @commands.command(name="whois")
    async def whois(self, ctx, node: hex_or_id):
        logger.info(f"Whois command received by: {ctx.author} for node: {node}")

        try:
            node = Node.get_or_none((Node.id == node[0]) | (Node.hex == node[1]))
        except Exception as e:
            logger.exception(e)
            await ctx.send(f"Error looking up node: {e}")

        if node:
            logger.debug(f"Node {node.id} found")
            content = f"Node ID **{node.id}** has the following known information and been seen **{node.sightings.count()}** times.\n"
            description = (
                "This node has no known owner." if not node.owner else f"This node appears to belong to {node.owner}"
            )
            hardware = "Unknown" if not node.hardware else node.hardware

            embed_info = (
                Embed(description=description, color=3850540)
                .add_field(name="ID", value=node.id, inline=True)
                .add_field(name="Hex", value=node.hex, inline=True)
                .add_field(name="Hardware", value=hardware, inline=True)
                .set_author(name=f"Node {node.id}")
            )

            if node.long_name:
                embed_info.add_field(name="Name", value=node.long_name, inline=True)

            embed_sightings = Embed(description=f"Recent sightings for **{node.id}**:", color=2328811)

            for sighting in node.sightings:
                discord_user = self.bot.get_user(sighting.user.discord_id)
                if discord_user:
                    discord_user_name = discord_user.display_name
                else:
                    discord_user_name = "Unknown"

                embed_sightings.add_field(name=discord_user_name, value=sighting.timestamp, inline=False)

            if node.sightings.count() == 0:
                embed_sightings.add_field(name="No sightings", value="This node has never been sighted.", inline=False)

            await ctx.send(content, embed=embed_info)
            await ctx.send(embed=embed_sightings)
        else:
            logger.debug(f"Node not found found")
            await ctx.send(f"Node not found.")

        await logger.complete()

    @commands.is_owner()
    @commands.command(name="create_database")
    async def create_database(self, ctx):
        logger.info("Creating database")
        try:
            models_created = create_tables()
        except Exception as e:
            logger.error(e)
            await ctx.send("Error creating database", e)
        await ctx.send(f"Database created with models: {models_created}")
        await logger.complete()

    @commands.is_owner()
    @commands.command(name="drop_database")
    async def drop_database(self, ctx):
        logger.info("Dropping database")
        try:
            User.drop_table()
            Node.drop_table()
            Sighting.drop_table()
        except Exception as e:
            logger.error(e)
            await ctx.send("Error dropping database", e)
        await ctx.send("Database dropped")
        await logger.complete()
