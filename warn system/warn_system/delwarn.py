import discord
import datetime
import aiosqlite
import asyncio
from discord.ext import commands
from discord import app_commands

class delwarn(commands.Cog):
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

    @app_commands.command(name = "delwarn", description = "Removes a members warning")
    @app_commands.checks.has_role(1154457410677788732)
    async def delwarn(self, interaction: discord.Interaction, id: int):
        async with self.db.cursor() as cursor:
            await cursor.execute("SELECT user FROM warns WHERE id = ? AND guild = ?", (id, interaction.guild.id))
            data = await cursor.fetchone()
            if data:
                await cursor.execute("DELETE FROM warns WHERE id = ? AND guild = ?", (id, interaction.guild.id))

                embed = discord.Embed(
                title = "Warn remove",
                description = f"Member´s <@{data[0]}> warning has been deleted.",
                color = discord.Color.red(),
                timestamp = datetime.datetime.utcnow()
                )
                await interaction.response.send_message(embed = embed)

            else:
                embed2 = discord.Embed(
                title = "Warn remove",
                description = f"ID **`{id}`** not found!",
                color = discord.Color.red(),
                timestamp = datetime.datetime.utcnow()
                )
                await interaction.response.send_message(embed = embed2)
                
        await self.db.commit()

    

async def setup(client: commands.Bot) -> None:
   await client.add_cog(delwarn(client))