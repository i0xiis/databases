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

class warns(commands.Cog):
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

    @app_commands.command(name = "warns", description = "Veiws a members warning")
    @app_commands.checks.has_role(1154457410677788732)
    async def warns(self, interaction: discord.Interaction, member: discord.Member):
        async with self.db.cursor() as cursor:
            await cursor.execute("SELECT moderator, id, reason, time FROM warns WHERE user = ? AND guild = ?", (member.id, interaction.guild.id))
            data = await cursor.fetchall()
            if data:
                embed = discord.Embed(
                    title = f"{member.name}´s warnings",
                    description = f"Here are all warnings of member {member.mention}",
                    color = discord.Color.blue(),
                    timestamp = datetime.datetime.utcnow()
                )         
                warnnum = 0
                for table in data:
                    warnnum += 1

                    moderator = table[0]
                    warnid = table[1]
                    reason = table[2]
                    date = int(table[3])

                    embed.add_field(
                        name = f"Warning {warnnum}",
                        value = f"Moderator: <@{moderator}>\nID: ```{warnid}```\nReason: {reason}\nDate issued: <t:{date}:F>",
                    )
                await interaction.response.send_message(embed = embed)
            else:
                embed2 = discord.Embed(
                    title = f"{member.name}´s warnings",
                    description = f"No warnings found!",
                    color = discord.Color.blue(),
                    timestamp = datetime.datetime.utcnow()
                )
                await interaction.response.send_message(embed = embed2)
        await self.db.commit()

    

async def setup(client: commands.Bot) -> None:
   await client.add_cog(warns(client))