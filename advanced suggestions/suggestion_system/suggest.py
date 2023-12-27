import discord
import datetime
import aiosqlite
import asyncio
from discord.ext import commands
from discord import app_commands, ui

class SuggestionModal(ui.Modal, title = "Submit a suggestion!"):
    aaa = ui.TextInput(label = "Title:", style = discord.TextStyle.short, placeholder = "The best suggestion you can imagine!", required = True, min_length = 5)
    suggestion = ui.TextInput(label = "Suggestion:", style = discord.TextStyle.short, placeholder = "Describe your best suggestion right here", required = True, min_length = 30)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title = self.aaa.label,
            description = self.aaa,
            color = discord.Color.blue(),
            timestamp = datetime.datetime.utcnow()
        )
        embed.add_field(
            name = self.suggestion.label,
            value = self.suggestion
        )
        await interaction.response.send_message(embed = embed)

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

    @app_commands.command(name = "suggest", description = "This is a test command")
    async def suggest(self, interaction: discord.Interaction, title: str, suggestion: str):

        author = interaction.user

        suggest = self.client.get_channel(1149003165337927680)

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

        suggmsg = await suggest.send(embed = suggEmbed)
        print(suggmsg)

        async with self.db.cursor() as cursor:
            await cursor.execute("INSERT INTO suggestions (author, title, suggestion, time, status, msg_id, guild) VALUES (?, ?, ?, ?, ?, ?, ?)", (author.id, title, suggestion, int(datetime.datetime.now().timestamp()), "None", suggmsg.id, interaction.guild.id))
        await self.db.commit()

        # await interaction.response.send_modal(SuggestionModal())

    # @app_commands.command(name = "suggest", description = "Makes a suggestion!")
    # async def suggest(self, interaction: discord.Interaction, title: str, suggestion: str):
    #     async with self.db.cursor() as cursor:
    #         await cursor.execute("SELECT moderator, id, reason, time FROM warns WHERE user = ? AND guild = ?", (member.id, interaction.guild.id))
    #         data = await cursor.fetchall()
    #         if data:
    #             embed = discord.Embed(
    #                 title = f"{member.name}´s warnings",
    #                 description = f"Here are all warnings of member {member.mention}",
    #                 color = discord.Color.blue(),
    #                 timestamp = datetime.datetime.utcnow()
    #             )         
    #             warnnum = 0
    #             for table in data:
    #                 warnnum += 1

    #                 moderator = table[0]
    #                 warnid = table[1]
    #                 reason = table[2]
    #                 date = int(table[3])

    #                 embed.add_field(
    #                     name = f"Warning {warnnum}",
    #                     value = f"Moderator: <@{moderator}>\nID: ```{warnid}```\nReason: {reason}\nDate issued: <t:{date}:F>",
    #                 )
    #             await interaction.response.send_message(embed = embed)
    #         else:
    #             embed2 = discord.Embed(
    #                 title = f"{member.name}´s warnings",
    #                 description = f"User {member.mention} has no warnings!",
    #                 color = discord.Color.blue(),
    #                 timestamp = datetime.datetime.utcnow()
    #             )
    #             await interaction.response.send_message(embed = embed2)
    #     await self.db.commit()

    # @suggest.error
    # async def on_ban_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        
    #     MissingPermissions = discord.Embed(
    #         title = "No permisions",
    #         color = discord.Color.yellow(),
    #         timestamp = datetime.datetime.utcnow()
    #     )
    #     MissingPermissions.add_field(
    #         name = ":shield: - Missing permissions",
    #         value = "*You don´t have permissions to use this command!*",
    #         inline = False
    #     )

    #     ErrorMessage = discord.Embed(
    #         title = "Error",
    #         color = discord.Color.yellow(),
    #         timestamp = datetime.datetime.utcnow()
    #     )
    #     ErrorMessage.add_field(
    #         name = ":space_invader: - Error",
    #         value = error,
    #         inline = False
    #     )
    #     ErrorMessage.add_field(
    #         name = ":envelope_with_arrow: - Reporting",
    #         value = "*Please go to https://discord.com/channels/1148996773826809936/1157374918929956986 and report this problem.*",
    #         inline = False
    #     )

    #     if isinstance(error, discord.app_commands.MissingRole):
    #         await interaction.response.send_message(embed = MissingPermissions, ephemeral = True)
    #     else:
    #         await interaction.response.send_message(embed = ErrorMessage, ephemeral = True)

    

async def setup(client: commands.Bot) -> None:
   await client.add_cog(suggest(client))