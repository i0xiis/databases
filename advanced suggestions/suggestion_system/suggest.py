import discord
import datetime
import aiosqlite
from discord.ext import commands
from discord import app_commands

from config import suggest_channel
from config import approval_channel
from config import tickets_channel_clv

from config import noemoji
from config import yesemoji
from config import wingman_siplink

from suggestion_system.views.approval_system import ApprovalSystem

        #! SUGGEST CLASS #

class suggest(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

        #* Database connection #

    async def connect_db(self):
        self.db = await aiosqlite.connect("suggestions.db")
        async with self.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS suggestions (id INTEGER PRIMARY KEY AUTOINCREMENT, author INTEGER, title TEXT, suggestion TEXT, status TEXT, msg_id INTEGER, log_id INTEGER, mod INTEGER, mod_comment TEXT, guild INTEGER)")
        await self.db.commit()

        #* Connecting to database #

    @commands.Cog.listener()
    async def on_ready(self):
        await self.connect_db()

        #* Suggest command #

    @app_commands.command(name = "suggest", description = "Makes a suggestion!")
    async def suggest(self, interaction: discord.Interaction, title: str, suggestion: str):

        author = interaction.user

        suggest = self.client.get_channel(suggest_channel)
        suggestlog = self.client.get_channel(approval_channel)

        await interaction.response.send_message(content = f"Suggestion called **{title}** has been posted!")

            #* Suggestion message #

        suggEmbed = discord.Embed(
            title = "Suggestion",
            description = f"*Here is a suggestion from user {author.mention}:*",
            color = discord.Color.yellow(),
            timestamp = datetime.datetime.utcnow()
        )
        suggEmbed.add_field(
            name = ":pencil: - Name of suggetion:",
            value = title,
            inline = False
        )
        suggEmbed.add_field(
            name = ":bulb: - Suggestion:",
            value = suggestion,
            inline = False
        )
        suggEmbed.set_thumbnail(url = wingman_siplink)

        suggmsg = await suggest.send(embed = suggEmbed)
        await suggmsg.add_reaction(yesemoji)
        await suggmsg.add_reaction(noemoji)

            #* Inserting data #

        async with self.db.cursor() as cursor:
            await cursor.execute("INSERT INTO suggestions (author, title, suggestion, status, msg_id, guild) VALUES (?, ?, ?, ?, ?, ?)", (author.id, title, suggestion, "waiting", suggmsg.id, interaction.guild.id))
        await self.db.commit()

        async with self.db.cursor() as cursor:
            await cursor.execute("SELECT id FROM suggestions WHERE msg_id = ? AND guild = ?", (suggmsg.id, interaction.guild.id))
            data = await cursor.fetchone()
            if data:
                s_id = data[0]

                    #* Log message #

                approval = discord.Embed(
                    title = "Suggestion log",
                    description = f"Suggestion log of {author.mention}",
                    color = discord.Color.yellow(),
                    timestamp = datetime.datetime.utcnow()
                )
                approval.add_field(
                    name = ":id: - Suggestion ID:",
                    value = f"```{s_id}```",
                    inline = False
                )
                approval.add_field(
                    name = ":pencil: - Name of suggetion:",
                    value = title,
                    inline = False
                )
                approval.add_field(
                    name = ":bulb: - Suggestion:",
                    value = suggestion,
                    inline = False
                )
                approval.set_thumbnail(url = wingman_siplink)

                logmsg = await suggestlog.send(embed = approval, view = ApprovalSystem(suggmsg.jump_url))

                await cursor.execute("UPDATE suggestions SET log_id = ? WHERE id = ? AND guild = ?", (logmsg.id, s_id, interaction.guild.id))

            else:
                return
            
            await self.db.commit()

        #* Error handling #

    @suggest.error
    async def on_suggest_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):

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
   await client.add_cog(suggest(client))