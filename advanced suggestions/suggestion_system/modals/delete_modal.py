import discord
import datetime
import aiosqlite
from discord import ui

from config import suggest_channel
from config import approval_channel

from config import noemojilink
from config import yesemojilink
from config import trashcanemoji
from config import trashcanemojilink

from suggestion_system.views.approval_system_disabled import ApprovalSystemDisabled

    #! DELETE MODAL #

class Delete(ui.Modal):

    def __init__(self):
        super().__init__(title = "Delete a suggestion!")

        #* Modal inputs #

    sugg_id = ui.TextInput(label = "Suggestion ID:", style = discord.TextStyle.short, placeholder = "Enter suggestion ID here", required = True)
    mod_comment = ui.TextInput(label = "Mod comment:", style = discord.TextStyle.long, placeholder = "Add your mod comment here (optional)", required = False, max_length = 500)

        #* On submit #

    async def on_submit(self, interaction: discord.Interaction):

        sugg_id = self.sugg_id.value
        mod_comment = self.mod_comment.value
        s_id = int(sugg_id)

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

                        suggestmsg = interaction.client.get_channel(suggest_channel)
                        sugg_msg = await suggestmsg.fetch_message(msg_id)

                        await sugg_msg.delete()

                            #* Log message #

                        delete = discord.Embed(
                            title = "Suggestion log",
                            description = f"Suggestion log of <@{author}>",
                            color = discord.Color.dark_blue(),
                            timestamp = datetime.datetime.utcnow()
                        )
                        delete.add_field(
                            name = ":id: - Suggestion ID:",
                            value = f"```{s_id}```",
                            inline = False
                        )
                        delete.add_field(
                            name = ":pencil: - Name of suggetion:",
                            value = title,
                            inline = False
                        )
                        delete.add_field(
                            name = ":bulb: - Suggestion:",
                            value = suggestion,
                            inline = False
                        )
                        delete.add_field(
                            name = f"{trashcanemoji} - Deleted:",
                            value = f"This suggestion has been deleted by {interaction.user.mention}!",
                            inline = False
                        )
                        if mod_comment:
                            delete.add_field(
                                name = f":speech_balloon: - Mod comment:",
                                value = mod_comment,
                                inline = False
                            )
                        else:
                            delete.add_field(
                                name = f":speech_balloon: - Mod comment:",
                                value = "-",
                                inline = False
                            )
                        delete.set_thumbnail(url = trashcanemojilink)

                        suggestlog = interaction.client.get_channel(approval_channel)
                        log_msg = await suggestlog.fetch_message(log_id)
                        
                        await log_msg.edit(embed = delete, view = ApprovalSystemDisabled(sugg_msg.jump_url))

                        await cursor.execute("UPDATE suggestions SET status = ?, mod = ?, mod_comment = ? WHERE id = ? AND guild = ?", ("deleted", interaction.user.id, mod_comment, s_id, interaction.guild.id))

                            #* Confirm message #
                        
                        embed = discord.Embed(
                            title = f"Suggestion deleted!",
                            description = f"Suggestion with ID {s_id} has been deleted.",
                            color = discord.Color.dark_blue(),
                            timestamp = datetime.datetime.utcnow()
                        )
                        embed.set_thumbnail(url = yesemojilink)
                        await interaction.response.send_message(embed = embed, ephemeral = True)

                        #* Already approved/denied/deleted #
                    
                    else:
                        embed = discord.Embed(
                            title = f"Suggestion delete",
                            description = f"Cannot delete suggestion **{s_id}**, suggestion is already {status}.",
                            color = discord.Color.red(),
                            timestamp = datetime.datetime.utcnow()
                        )
                        embed.set_thumbnail(url = noemojilink)
                        await interaction.response.send_message(embed = embed, ephemeral = True)

                else:

                        #* ID not found #
                    
                    embed = discord.Embed(
                        title = f"Suggestion delete",
                        description = f"ID {s_id} not found..",
                        color = discord.Color.red(),
                        timestamp = datetime.datetime.utcnow()
                    )
                    embed.set_thumbnail(url = noemojilink)
                    await interaction.response.send_message(embed = embed, ephemeral = True)

            await db.commit()