import discord
import datetime
import aiosqlite
from discord import ui

from config import noemoji
from config import noemojilink
from config import yesemoji
from config import yesemojilink
from config import wingman_sad

from suggestion_system.views.approval_system_disabled import ApprovalSystemDisabled

    #! DENY MODAL #

class Deny(ui.Modal):

    def __init__(self):
        super().__init__(title = "Deny a suggestion!")

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
        
            #* Getting channels #
        
        async with aiosqlite.connect("main.db") as datadb:
            async with datadb.cursor() as datacursor:
                await datacursor.execute("SELECT sugg_channel, log_channel FROM channels WHERE guild = ?", (interaction.guild.id,))
                data = await datacursor.fetchone()
                if data:
                    
                    sugg_channel = data[0]
                    log_channel = data[1]

                        #* Database connection #

                    async with aiosqlite.connect("main.db") as db:
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

                                    deniedSuggmsg = discord.Embed(
                                        title = "Denied suggestion!",
                                        description = f"*Here is the **denied** suggestion from user <@{author}>:*",
                                        color = discord.Color.red(),
                                        timestamp = datetime.datetime.utcnow()
                                    )
                                    deniedSuggmsg.add_field(
                                        name = ":pencil: - Name of suggetion:",
                                        value = title,
                                        inline = False
                                    )
                                    deniedSuggmsg.add_field(
                                        name = ":bulb: - Suggestion:",
                                        value = suggestion,
                                        inline = False
                                    )
                                    deniedSuggmsg.add_field(
                                        name = f"{yesemoji} - Denied:",
                                        value = f"This suggestion has been denied by {interaction.user.mention}!",
                                        inline = False
                                    )
                                    if mod_comment:
                                        deniedSuggmsg.add_field(
                                            name = f":speech_balloon: - Mod comment:",
                                            value = mod_comment,
                                            inline = False
                                        )
                                    else:
                                        deniedSuggmsg.add_field(
                                            name = f":speech_balloon: - Mod comment:",
                                            value = "-",
                                            inline = False
                                        )
                                    deniedSuggmsg.set_thumbnail(url = noemojilink)

                                    suggestmsg = interaction.client.get_channel(sugg_channel)
                                    sugg_msg = await suggestmsg.fetch_message(msg_id)

                                    await sugg_msg.edit(embed = deniedSuggmsg)

                                    await sugg_msg.clear_reactions()
                                    await sugg_msg.add_reaction(wingman_sad)

                                        #* Log message #

                                    deny = discord.Embed(
                                        title = "Suggestion log",
                                        description = f"Suggestion log of <@{author}>",
                                        color = discord.Color.red(),
                                        timestamp = datetime.datetime.utcnow()
                                    )
                                    deny.add_field(
                                        name = ":id: - Suggestion ID:",
                                        value = f"```{s_id}```",
                                        inline = False
                                    )
                                    deny.add_field(
                                        name = ":pencil: - Name of suggetion:",
                                        value = title,
                                        inline = False
                                    )
                                    deny.add_field(
                                        name = ":bulb: - Suggestion:",
                                        value = suggestion,
                                        inline = False
                                    )
                                    deny.add_field(
                                        name = f"{noemoji} - Denied:",
                                        value = f"This suggestion has been denied by {interaction.user.mention}!",
                                        inline = False
                                    )
                                    if mod_comment:
                                        deny.add_field(
                                            name = f":speech_balloon: - Mod comment:",
                                            value = mod_comment,
                                            inline = False
                                        )
                                    else:
                                        deny.add_field(
                                            name = f":speech_balloon: - Mod comment:",
                                            value = "-",
                                            inline = False
                                        )
                                    deny.set_thumbnail(url = noemojilink)

                                    suggestlog = interaction.client.get_channel(log_channel)
                                    log_msg = await suggestlog.fetch_message(log_id)
                                    
                                    await log_msg.edit(embed = deny, view = ApprovalSystemDisabled(sugg_msg.jump_url))

                                    await cursor.execute("UPDATE suggestions SET status = ?, mod = ?, mod_comment = ? WHERE id = ? AND guild = ?", ("denied", interaction.user.id, mod_comment, s_id, interaction.guild.id))

                                        #* Confirm message #
                                    
                                    embed = discord.Embed(
                                        title = f"Suggestion denied!",
                                        description = f"Suggestion with ID {s_id} has been denied.",
                                        color = discord.Color.red(),
                                        timestamp = datetime.datetime.utcnow()
                                    )
                                    embed.set_thumbnail(url = yesemojilink)
                                    await interaction.response.send_message(embed = embed, ephemeral = True)

                                    #* Already approved/denied/deleted #
                                
                                else:
                                    embed = discord.Embed(
                                        title = f"Suggestion deny",
                                        description = f"Cannot deny suggestion **{s_id}**, suggestion is already {status}.",
                                        color = discord.Color.red(),
                                        timestamp = datetime.datetime.utcnow()
                                    )
                                    embed.set_thumbnail(url = noemojilink)
                                    await interaction.response.send_message(embed = embed, ephemeral = True)

                            else:

                                    #* ID not found #
                                
                                embed = discord.Embed(
                                    title = f"Suggestion deny",
                                    description = f"ID {s_id} not found..",
                                    color = discord.Color.red(),
                                    timestamp = datetime.datetime.utcnow()
                                )
                                embed.set_thumbnail(url = noemojilink)
                                await interaction.response.send_message(embed = embed, ephemeral = True)

                        await db.commit()
                else:
                    return