import discord
import datetime
import aiosqlite
from discord.ext import commands
from discord import app_commands, ui
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

class Approve(ui.Modal):

    def __init__(self):
        super().__init__(title = "Approve a suggestion!")

    sugg_id = ui.TextInput(label = "Suggestion ID:", style = discord.TextStyle.short, placeholder = "11", required = True)
    mod_comment = ui.TextInput(label = "Mod comment:", style = discord.TextStyle.long, placeholder = "Add your mod comment here", required = False, max_length = 500)

    

    async def on_submit(self, interaction: discord.Interaction):

        sugg_id = self.sugg_id.value
        mod_comment = self.mod_comment.value
        s_id = int(sugg_id)
        async with aiosqlite.connect("suggestions.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT author, title, suggestion, msg_id, log_id FROM suggestions WHERE id = ? AND guild = ?", (s_id, interaction.guild.id))
                data = await cursor.fetchone()
                if data:

                    author = data[0]
                    title = data[1]
                    suggestion = data[2]
                    msg_id = data[3]
                    log_id = data[4]

                    approve = discord.Embed(
                        title = "Suggestion log",
                        description = f"Suggestion log of <@{author}>",
                        color = discord.Color.dark_green(),
                        timestamp = datetime.datetime.utcnow()
                    )
                    approve.add_field(
                        name = ":id: - Suggestion ID:",
                        value = f"```{s_id}```",
                        inline = False
                    )
                    approve.add_field(
                        name = ":pencil: - Name of suggetion:",
                        value = title,
                        inline = False
                    )
                    approve.add_field(
                        name = ":bulb: - Suggestion:",
                        value = suggestion,
                        inline = False
                    )
                    approve.add_field(
                        name = f"{yesemoji} - Approved:",
                        value = f"This suggestion has been approved by {interaction.user.mention}!",
                        inline = False
                    )
                    if mod_comment != None:
                        approve.add_field(
                            name = f":speech_balloon: - Mod comment:",
                            value = mod_comment,
                            inline = False
                        )
                    else:
                        pass
                    approve.set_thumbnail(url = yesemojilink)
                    
                    suggestlog = interaction.client.get_channel(approval_channel)
                    log_msg = await suggestlog.fetch_message(log_id)
                    await log_msg.edit(embed = approve, view = self)
                
                    await cursor.execute("UPDATE suggestions SET status = ?, mod = ?, mod_comment = ? WHERE id = ? AND guild = ?", ("Approved", interaction.user.id, mod_comment, s_id, interaction.guild.id))

                else:
                    embed = discord.Embed(
                        title = f"Suggestion approve",
                        description = f"ID {s_id} not found..",
                        color = discord.Color.red(),
                        timestamp = datetime.datetime.utcnow()
                    )
                    await interaction.response.send_message(embed = embed, ephemeral = True)

                await db.commit()

class ApprovalSystem(discord.ui.View):
    def __init__(self, suggmsg, url, title, author, suggestion):
        self.suggmsg = suggmsg
        self.url = url
        self.title = title
        self.author = author
        self.suggestion = suggestion
        super().__init__(timeout = None)
        self.add_item(Button(label = "Jump to suggestion", style = discord.ButtonStyle.gray, url = self.url))

    @discord.ui.button(label = "Approve", style = discord.ButtonStyle.green, emoji = yesemoji, custom_id = "approve")
    async def Approve(self, interaction: discord.Interaction, button: discord.Button):

        self.Approve.disabled = True 
        self.Deny.disabled = True 
        self.Delete.disabled = True

        await interaction.response.send_modal(Approve())

        # approve = discord.Embed(
        #     title = "Suggestion log",
        #     description = f"Suggestion log of {self.author.mention}",
        #     color = discord.Color.dark_green(),
        #     timestamp = datetime.datetime.utcnow()
        # )
        # approve.add_field(
        #     name = ":pencil: - Name of suggetion:",
        #     value = self.title,
        #     inline = False
        # )
        # approve.add_field(
        #     name = ":bulb: - Suggestion:",
        #     value = self.suggestion,
        #     inline = False
        # )
        # approve.add_field(
        #     name = f"{yesemoji} - Approved:",
        #     value = f"This suggestion has been approved by {interaction.user.mention}!",
        #     inline = False
        # )
        # approve.set_thumbnail(url = yesemojilink)

        # await interaction.response.edit_message(embed = approve, view = self)

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
        async with self.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS suggestions (id INTEGER PRIMARY KEY AUTOINCREMENT, author INTEGER, title TEXT, suggestion TEXT, status TEXT, msg_id INTEGER, log_id INTEGER, mod INTEGER, mod_comment TEXT, guild INTEGER)")
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

        logmsg = await suggestlog.send(embed = approval, view = ApprovalSystem(suggmsg, suggmsg.jump_url, title, author, suggestion))

        async with self.db.cursor() as cursor:
            await cursor.execute("INSERT INTO suggestions (author, title, suggestion, status, msg_id, log_id, guild) VALUES (?, ?, ?, ?, ?, ?, ?)", (author.id, title, suggestion, "Waiting..", suggmsg.id, logmsg.id, interaction.guild.id))
        await self.db.commit()
    
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