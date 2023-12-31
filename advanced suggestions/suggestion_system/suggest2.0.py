import discord
import datetime
import aiosqlite
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import Button

from config import suggest_channel
from config import approval_channel
from config import tickets_channel_clv

from config import noemoji
from config import noemojilink
from config import yesemoji
from config import yesemojilink
from config import trashcanemoji
from config import trashcanemojilink
from config import wingman_love
from config import wingman_sad
from config import wingman_siplink

class ApprovalSystem(discord.ui.View):
    def __init__(self, suggmsg, url, title, author, suggestion):
        self.suggmsg = suggmsg
        self.url = url
        self.title = title
        self.author = author
        self.suggestion = suggestion
        super().__init__(timeout = None)
        self.add_item(Button(label = "Jump to suggestion", style = discord.ButtonStyle.gray, url = self.url))

    async def connect_db(self, interaction, member):
        async with self.db.cursor() as cursor:
            await cursor.execute("SELECT title, suggestion, time, msg_id FROM warns WHERE author = ? AND guild = ?", (member.id, interaction.guild.id))
            data = await cursor.fetchall()

    @discord.ui.button(label = "Approve", style = discord.ButtonStyle.green, emoji = yesemoji, custom_id = "approve")
    async def Approve(self, interaction: discord.Interaction, button: discord.Button):

        self.Approve.disabled = True 
        self.Deny.disabled = True 
        self.Delete.disabled = True

        approve = discord.Embed(
            title = "Suggestion log",
            description = f"Suggestion log of {self.author.mention}",
            color = discord.Color.dark_green(),
            timestamp = datetime.datetime.utcnow()
        )
        approve.add_field(
            name = ":pencil: - Name of suggetion:",
            value = self.title,
            inline = False
        )
        approve.add_field(
            name = ":bulb: - Suggestion:",
            value = self.suggestion,
            inline = False
        )
        approve.add_field(
            name = f"{yesemoji} - Approved:",
            value = f"This suggestion has been approved by {interaction.user.mention}!",
            inline = False
        )
        approve.set_thumbnail(url = yesemojilink)

        await interaction.response.edit_message(embed = approve, view = self)

        approvedSuggmsg = discord.Embed(
            title = "Approved suggestion!",
            description = f"*Here is the **approved** suggestion from user {self.author.mention}:*",
            color = discord.Color.dark_green(),
            timestamp = datetime.datetime.utcnow()
        )
        approvedSuggmsg.add_field(
            name = ":pencil: - Name of suggetion:",
            value = self.title,
            inline = False
        )
        approvedSuggmsg.add_field(
            name = ":bulb: - Suggestion:",
            value = self.suggestion,
            inline = False
        )
        approvedSuggmsg.add_field(
            name = f"{yesemoji} - Approved:",
            value = f"This suggestion has been approved by {interaction.user.mention}!",
            inline = False
        )
        approvedSuggmsg.set_thumbnail(url = yesemojilink)

        await self.suggmsg.edit(embed = approvedSuggmsg)

        await self.suggmsg.clear_reactions()
        await self.suggmsg.add_reaction(wingman_love)

    @discord.ui.button(label = "Deny", style = discord.ButtonStyle.red, emoji = noemoji, custom_id = "deny")
    async def Deny(self, interaction: discord.Interaction, Button: discord.Button):

        self.Approve.disabled = True 
        self.Deny.disabled = True 
        self.Delete.disabled = True

        deny = discord.Embed(
            title = "Suggestion log",
            description = f"Suggestion log of {self.author.mention}",
            color = discord.Color.red(),
            timestamp = datetime.datetime.utcnow()
        )
        deny.add_field(
            name = ":pencil: - Name of suggetion:",
            value = self.title,
            inline = False
        )
        deny.add_field(
            name = ":bulb: - Suggestion:",
            value = self.suggestion,
            inline = False
        )
        deny.add_field(
            name = f"{noemoji} - Denied:",
            value = f"This suggestion has been denied by {interaction.user.mention}!",
            inline = False
        )
        deny.set_thumbnail(url = noemojilink)

        await interaction.response.edit_message(embed = deny, view = self)

        deniedSuggmsg = discord.Embed(
            title = "Denied suggestion!",
            description = f"*Here is the **denied** suggestion from user {self.author.mention}:*",
            color = discord.Color.red(),
            timestamp = datetime.datetime.utcnow()
        )
        deniedSuggmsg.add_field(
            name = ":pencil: - Name of suggetion:",
            value = self.title,
            inline = False
        )
        deniedSuggmsg.add_field(
            name = ":bulb: - Suggestion:",
            value = self.suggestion,
            inline = False
        )
        deniedSuggmsg.add_field(
            name = f"{noemoji} - Denied:",
            value = f"This suggestion has been denied by {interaction.user.mention}!",
            inline = False
        )
        deniedSuggmsg.set_thumbnail(url = noemojilink)

        await self.suggmsg.edit(embed = deniedSuggmsg)

        await self.suggmsg.clear_reactions()
        await self.suggmsg.add_reaction(wingman_sad)

    @discord.ui.button(label = "Delete", style = discord.ButtonStyle.red, emoji = trashcanemoji, custom_id = "delete")
    async def Delete(self, interaction: discord.Interaction, Button: discord.Button):

        self.Approve.disabled = True 
        self.Deny.disabled = True 
        self.Delete.disabled = True

        delete = discord.Embed(
            title = "Suggestion log",
            description = f"Suggestion log of {self.author.mention}",
            color = discord.Color.dark_blue(),
            timestamp = datetime.datetime.utcnow()
        )
        delete.add_field(
            name = ":pencil: - Name of suggetion:",
            value = self.title,
            inline = False
        )
        delete.add_field(
            name = ":bulb: - Suggestion:",
            value = self.suggestion,
            inline = False
        )
        delete.add_field(
            name = f"{trashcanemoji} - Deleted:",
            value = f"This suggestion has been deleted by {interaction.user.mention}!",
            inline = False
        )
        delete.set_thumbnail(url = trashcanemojilink)

        await self.suggmsg.delete()

        await interaction.response.edit_message(embed = delete, view = self)


class suggest(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    async def connect_db(self):
        self.db = await aiosqlite.connect("suggestions.db")
        await asyncio.sleep(1)
        async with self.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS suggestions (id INTEGER PRIMARY KEY AUTOINCREMENT, author INTEGER, title TEXT, suggestion TEXT, time INTEGER, status TEXT, msg_id INTEGER, guild INTEGER)")
        await self.db.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.connect_db()

    @app_commands.command(name = "suggest", description = "Makes a suggestion!")
    async def suggest(self, interaction: discord.Interaction, title: str, suggestion: str):

        author = interaction.user

        suggest = self.client.get_channel(suggest_channel)
        suggestlog = self.client.get_channel(approval_channel)

        await interaction.response.send_message(content = f"Suggestion called **{title}** has been posted!")

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

        async with self.db.cursor() as cursor:
            await cursor.execute("INSERT INTO suggestions (author, title, suggestion, time, status, msg_id, guild) VALUES (?, ?, ?, ?, ?, ?, ?)", (author.id, title, suggestion, int(datetime.datetime.now().timestamp()), "None", suggmsg.id, interaction.guild.id))
        await self.db.commit()

        approval = discord.Embed(
            title = "Suggestion log",
            description = f"Suggestion log of {author.mention}",
            color = discord.Color.yellow(),
            timestamp = datetime.datetime.utcnow()
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

        await suggestlog.send(embed = approval, view = ApprovalSystem(suggmsg, suggmsg.jump_url, title, author, suggestion))
    
    @suggest.error
    async def on_suggest_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        
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