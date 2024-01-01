import discord
from discord.ui import Button

from config import noemoji
from config import yesemoji
from config import trashcanemoji

    #! APPROVAL SYSTEM - DISABLED #

class ApprovalSystemDisabled(discord.ui.View):
    def __init__(self, url):
        self.url = url
        super().__init__(timeout = None)

            #* Display buttons - disabled #

        self.add_item(Button(label = "Approve", style = discord.ButtonStyle.green, emoji = yesemoji, disabled = True))
        self.add_item(Button(label = "Deny", style = discord.ButtonStyle.red, emoji = noemoji, disabled = True))
        self.add_item(Button(label = "Delete", style = discord.ButtonStyle.red, emoji = trashcanemoji, disabled = True))
        self.add_item(Button(label = "Jump to suggestion", style = discord.ButtonStyle.gray, url = self.url))