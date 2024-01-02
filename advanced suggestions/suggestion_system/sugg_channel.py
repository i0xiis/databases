import discord
import datetime
import aiosqlite
from discord.ext import commands
from discord import app_commands

from config import tickets_channel_clv

from config import noemoji
from config import yesemoji
from config import yesemojilink

class sugg_channel(commands.Cog):
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

    @app_commands.command(name = "sugg_channel", description = "Sets a suggestion channel.")
    @app_commands.checks.has_role(1154457410677788732)
    async def sugg_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):

        async with aiosqlite.connect("main.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT sugg_channel FROM channels WHERE guild = ?", (interaction.guild.id,))
                data = await cursor.fetchone()
                if data:

                    current_channel = data[0]

                    if current_channel:

                        if current_channel == channel.id:
                            embed = discord.Embed(
                                title = "Suggestion channel setup",
                                description = f"This channel is already set up as suggestion channel!",
                                color = discord.Color.yellow(),
                                timestamp = datetime.datetime.utcnow()
                            )
                            embed.add_field(
                                name = f"{yesemoji} - Current channel:",
                                value = f"<#{channel.id}>"
                            )
                            await interaction.response.send_message(embed = embed)

                        else:
                            await cursor.execute("UPDATE channels SET sugg_channel = ? WHERE guild = ?", (channel.id, interaction.guild.id))

                            embed = discord.Embed(
                                title = "Suggestion channel setup",
                                description = f"Suggestion channel has been updated!",
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
                        await cursor.execute("UPDATE channels SET sugg_channel = ? WHERE guild = ?", (channel.id, interaction.guild.id))

                        embed = discord.Embed(
                            title = "Suggestion channel setup",
                            description = f"Suggestion channel has been set up!",
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
                    await cursor.execute("INSERT INTO channels (sugg_channel, guild) VALUES (?, ?)", (channel.id, interaction.guild.id,))

                    embed = discord.Embed(
                        title = "Suggestion channel setup",
                        description = f"Suggestion channel has been set up!",
                        color = discord.Color.dark_green(),
                        timestamp = datetime.datetime.utcnow()
                    )
                    embed.add_field(
                        name = f"{yesemoji} - Current channel:",
                        value = f"<#{channel.id}>",
                        inline = False
                    )
                    embed.add_field(
                        name = f":white_check_mark: - Log channel setup:",
                        value = f"</log_channel:1191540158961553461>",
                        inline = False
                    )
                    embed.set_thumbnail(url = yesemojilink)
                    await interaction.response.send_message(embed = embed)

            await db.commit()

        #* Error handling #

    @sugg_channel.error
    async def on_sugg_channel_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):

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
   await client.add_cog(sugg_channel(client))