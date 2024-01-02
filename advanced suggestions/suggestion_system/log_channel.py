import discord
import datetime
import aiosqlite
from discord.ext import commands
from discord import app_commands

from config import tickets_channel_clv

from config import noemoji
from config import yesemoji
from config import yesemojilink

class log_channel(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

        #* Database connection #

    async def connect_db(self):
        self.db = await aiosqlite.connect("main.db")
        async with self.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS channels (sugg_channel INTEGER, log_channel INTEGER, guild INTEGER)")
        await self.db.commit()

        #* Connecting to database #

    @commands.Cog.listener()
    async def on_ready(self):
        await self.connect_db()

        #* Suggest channel command #

    @app_commands.command(name = "log_channel", description = "Sets a log channel.")
    @app_commands.checks.has_role(1154457410677788732)
    async def log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):

        async with aiosqlite.connect("main.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT log_channel FROM channels WHERE guild = ?", (interaction.guild.id,))
                data = await cursor.fetchone()
                if data:

                    current_channel = data[0]

                    if current_channel:

                        if current_channel == channel.id:
                            embed = discord.Embed(
                                title = "Log channel setup",
                                description = f"This channel is already set up as log channel!",
                                color = discord.Color.yellow(),
                                timestamp = datetime.datetime.utcnow()
                            )
                            embed.add_field(
                                name = f"{yesemoji} - Current channel:",
                                value = f"<#{channel.id}>"
                            )
                            await interaction.response.send_message(embed = embed)

                        else:
                            await cursor.execute("UPDATE channels SET log_channel = ? WHERE guild = ?", (channel.id, interaction.guild.id))

                            embed = discord.Embed(
                                title = "Log channel setup",
                                description = f"Log channel has been updated!",
                                color = discord.Color.orange(),
                                timestamp = datetime.datetime.utcnow()
                            )
                            embed.add_field(
                                name = f"{noemoji} - Old channel:",
                                value = f"<#{current_channel}>"
                            )
                            embed.add_field(
                                name = f"{yesemoji} - New channel:",
                                value = f"<#{channel.id}>"
                            )
                            embed.set_thumbnail(url = yesemojilink)
                            await interaction.response.send_message(embed = embed)
                        
                    else:
                        await cursor.execute("UPDATE channels SET log_channel = ? WHERE guild = ?", (channel.id, interaction.guild.id))

                        embed = discord.Embed(
                            title = "Log channel setup",
                            description = f"Log channel has been set up!",
                            color = discord.Color.dark_green(),
                            timestamp = datetime.datetime.utcnow()
                        )
                        embed.add_field(
                            name = f"{yesemoji} - Current channel:",
                            value = f"<#{channel.id}>"
                        )
                        embed.set_thumbnail(url = yesemojilink)
                        await interaction.response.send_message(embed = embed)
                
                else:
                    await cursor.execute("INSERT INTO channels (log_channel, guild) VALUES (?, ?)", (channel.id, interaction.guild.id,))

                    embed = discord.Embed(
                        title = "Log channel setup",
                        description = f"Log channel has been set up!",
                        color = discord.Color.dark_green(),
                        timestamp = datetime.datetime.utcnow()
                    )
                    embed.add_field(
                        name = f"{yesemoji} - Current channel:",
                        value = f"<#{channel.id}>",
                        inline = False
                    )
                    embed.add_field(
                        name = f":bulb: - Suggestion channel setup:",
                        value = f"</sugg_channel:1191528114208124951>",
                        inline = False
                    )
                    embed.set_thumbnail(url = yesemojilink)
                    await interaction.response.send_message(embed = embed)

            await db.commit()

        #* Error handling #

    @log_channel.error
    async def on_log_channel_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):

            #* Missing permissions #
        
        MissingPermissions = discord.Embed(
            title = "No permisions",
            color = discord.Color.yellow(),
            timestamp = datetime.datetime.utcnow()
        )
        MissingPermissions.add_field(
            name = ":shield: - Missing permissions",
            value = "*You don´t have permissions to use this command!*",
            inline = False
        )

            #* Other errors #

        ErrorMessage = discord.Embed(
            title = "Error",
            color = discord.Color.yellow(),
            timestamp = datetime.datetime.utcnow()
        )
        ErrorMessage.add_field(
            name = ":space_invader: - Error",
            value = error,
            inline = False
        )
        ErrorMessage.add_field(
            name = ":envelope_with_arrow: - Reporting",
            value = f"*Please go to {tickets_channel_clv} and report this problem.*",
            inline = False
        )

        if isinstance(error, discord.app_commands.MissingRole):
            await interaction.response.send_message(embed = MissingPermissions, ephemeral = True)
        else:
            await interaction.response.send_message(embed = ErrorMessage, ephemeral = True)


async def setup(client: commands.Bot) -> None:
   await client.add_cog(log_channel(client))