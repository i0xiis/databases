import discord
import datetime
import aiosqlite
from discord import ui

from config import suggest_channel
from config import approval_channel

from config import noemojilink
from config import yesemoji
from config import yesemojilink
from config import wingman_love

from suggestion_system.views.approval_system_disabled import ApprovalSystemDisabled

    #! APPROVE MODAL #

class Approve(ui.Modal):

    def __init__(self):
        super().__init__(title = "Approve a suggestion!")

        #* Modal inputs #

    sugg_id = ui.TextInput(label = "Suggestion ID:", style = discord.TextStyle.short, placeholder = "Enter suggestion ID here", required = True)
    mod_comment = ui.TextInput(label = "Mod comment:", style = discord.TextStyle.long, placeholder = "Add your mod comment here (optional)", required = False, max_length = 500)

        #* On submit #

    async def on_submit(self, interaction: discord.Interaction):

        sugg_id = self.sugg_id.value
        mod_comment = self.mod_comment.value

            #* Convert id to int #
        
        try:
            s_id = int(sugg_id)
        except:
            embed = discord.Embed(
                title = f"ID is not a number",
                description = f"{sugg_id} is not a nuber..",
                color = discord.Color.red(),
                timestamp = datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url = noemojilink)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

            #* Database connection #

        async with aiosqlite.connect("suggestions.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT author, title, suggestion, msg_id, log_id, status FROM suggestions WHERE id = ? AND guild = ?", (s_id, interaction.guild.id))
                data = await cursor.fetchone()
                if data:

                    author = data[0]
                    title = data[1]
                    suggestion = data[2]
                    msg_id = data[3]
                    log_id = data[4]
                    status = data[5]

                    if status == "waiting":

                            #* Suggestion messaage #

                        approvedSuggmsg = discord.Embed(
                            title = "Approved suggestion!",
                            description = f"*Here is the **approved** suggestion from user <@{author}>:*",
                            color = discord.Color.dark_green(),
                            timestamp = datetime.datetime.utcnow()
                        )
                        approvedSuggmsg.add_field(
                            name = ":pencil: - Name of suggetion:",
                            value = title,
                            inline = False
                        )
                        approvedSuggmsg.add_field(
                            name = ":bulb: - Suggestion:",
                            value = suggestion,
                            inline = False
                        )
                        approvedSuggmsg.add_field(
                            name = f"{yesemoji} - Approved:",
                            value = f"This suggestion has been approved by {interaction.user.mention}!",
                            inline = False
                        )
                        if mod_comment:
                            approvedSuggmsg.add_field(
                                name = f":speech_balloon: - Mod comment:",
                                value = mod_comment,
                                inline = False
                            )
                        else:
                            approvedSuggmsg.add_field(
                                name = f":speech_balloon: - Mod comment:",
                                value = "-",
                                inline = False
                            )
                        approvedSuggmsg.set_thumbnail(url = yesemojilink)

                        suggestmsg = interaction.client.get_channel(suggest_channel)
                        sugg_msg = await suggestmsg.fetch_message(msg_id)

                        await sugg_msg.edit(embed = approvedSuggmsg)

                        await sugg_msg.clear_reactions()
                        await sugg_msg.add_reaction(wingman_love)

                            #* Log message #

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
                        if mod_comment:
                            approve.add_field(
                                name = f":speech_balloon: - Mod comment:",
                                value = mod_comment,
                                inline = False
                            )
                        else:
                            approve.add_field(
                                name = f":speech_balloon: - Mod comment:",
                                value = "-",
                                inline = False
                            )
                        approve.set_thumbnail(url = yesemojilink)

                        suggestlog = interaction.client.get_channel(approval_channel)
                        log_msg = await suggestlog.fetch_message(log_id)
                        
                        await log_msg.edit(embed = approve, view = ApprovalSystemDisabled(sugg_msg.jump_url))

                        await cursor.execute("UPDATE suggestions SET status = ?, mod = ?, mod_comment = ? WHERE id = ? AND guild = ?", ("approved", interaction.user.id, mod_comment, s_id, interaction.guild.id))

                            #* Confirm message #
                        
                        embed = discord.Embed(
                            title = f"Suggestion approved!",
                            description = f"Suggestion with ID {s_id} has been approved.",
                            color = discord.Color.dark_green(),
                            timestamp = datetime.datetime.utcnow()
                        )
                        embed.set_thumbnail(url = yesemojilink)
                        await interaction.response.send_message(embed = embed, ephemeral = True)

                        #* Already approved/denied/deleted #

                    else:
                        embed = discord.Embed(
                            title = f"Suggestion approve",
                            description = f"Cannot approve suggestion **{s_id}**, suggestion is already {status}.",
                            color = discord.Color.red(),
                            timestamp = datetime.datetime.utcnow()
                        )
                        embed.set_thumbnail(url = noemojilink)
                        await interaction.response.send_message(embed = embed, ephemeral = True)

                else:

                        #* ID not found #
                    
                    embed = discord.Embed(
                        title = f"Suggestion approve",
                        description = f"ID {s_id} not found..",
                        color = discord.Color.red(),
                        timestamp = datetime.datetime.utcnow()
                    )
                    embed.set_thumbnail(url = noemojilink)
                    await interaction.response.send_message(embed = embed, ephemeral = True)

            await db.commit()