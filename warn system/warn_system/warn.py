import discord
import datetime
import aiosqlite
import asyncio
from discord.ext import commands
from discord import app_commands

async def addwarn(self, interaction, reason, user):
    async with self.db.cursor() as cursor:
        await cursor.execute("INSERT INTO warns (user, reason, time, guild, moderator) VALUES (?, ?, ?, ?, ?)", (user.id, reason, int(datetime.datetime.now().timestamp()), interaction.guild.id, interaction.user.id))
    await self.db.commit()

class warn(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    async def connect_db(self):
        self.db = await aiosqlite.connect("warns.db")
        await asyncio.sleep(1)
        async with self.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS warns (id INTEGER PRIMARY KEY AUTOINCREMENT, user INTEGER, reason TEXT, time INTEGER, guild INTEGER, moderator INTEGER)")
        await self.db.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.connect_db()

    @app_commands.command(name = "warn", description = "Warns a member")
    @app_commands.checks.has_role(1154457410677788732)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
            
        await addwarn(self, interaction, reason, member)

        embed = discord.Embed(
            title = "Warn",
            description = f"Member {member.mention} has been warned.\nReason: *{reason}*",
            color = discord.Color.red(),
            timestamp = datetime.datetime.utcnow()
        )
        await interaction.response.send_message(embed = embed)

    

async def setup(client: commands.Bot) -> None:
   await client.add_cog(warn(client))