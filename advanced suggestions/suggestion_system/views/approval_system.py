import discord
from discord.ui import Button

from config import noemoji
from config import yesemoji
from config import trashcanemoji

from suggestion_system.modals.approve_modal import Approve
from suggestion_system.modals.deny_modal import Deny
from suggestion_system.modals.delete_modal import Delete

    #! APPROVAL SYSTEM #

class ApprovalSystem(discord.ui.View):
    def __init__(self, url):
        self.url = url
        super().__init__(timeout = None)
        self.add_item(Button(label = "Jump to suggestion", style = discord.ButtonStyle.gray, url = self.url))

        #* Approve button #

    @discord.ui.button(label = "Approve", style = discord.ButtonStyle.green, emoji = yesemoji, custom_id = "approve")
    async def Approve(self, interaction: discord.Interaction, button: discord.Button):

        await interaction.response.send_modal(Approve())

        #* Deny button #

    @discord.ui.button(label = "Deny", style = discord.ButtonStyle.red, emoji = noemoji, custom_id = "deny")
    async def Deny(self, interaction: discord.Interaction, Button: discord.Button):

        await interaction.response.send_modal(Deny())

        #* Delete button #

    @discord.ui.button(label = "Delete", style = discord.ButtonStyle.red, emoji = trashcanemoji, custom_id = "delete")
    async def Delete(self, interaction: discord.Interaction, Button: discord.Button):

        await interaction.response.send_modal(Delete())