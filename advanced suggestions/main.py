import discord
import json
import time
from discord.ext import commands
from colorama import Back, Fore, Style

command_list = ["suggestion_system.suggest3"]

class Client(commands.Bot):
  def __init__(self):
    intents = discord.Intents().all()
    super().__init__(command_prefix = commands.when_mentioned_or("~"), intents = intents)
    self.command_list = command_list
    
  async def setup_hook(self):

    for ext in self.command_list:
        await self.load_extension(ext)

  async def on_ready(self):
    cmdprfx = (Back.BLACK + Fore.BLUE + time.strftime("%H:%M:%S UTC+2", time.gmtime(time.time() + 7200)) + Back.RESET + Fore.WHITE + Style.BRIGHT + Back.RESET)

    print(cmdprfx + " Logged in as " + Fore.YELLOW + client.user.name)
    print(cmdprfx + " Bot ID " + Fore.YELLOW + str(client.user.id))
    print(cmdprfx + " Discord Version " + Fore.YELLOW + discord.__version__)
    try:
        synced = await client.tree.sync()
        print(cmdprfx + " Slash Commands Synced " + Fore.YELLOW + str(len(synced)) + " Commands")
    except Exception as e:
        print(e)
    await client.change_presence(activity = discord.Game("Leave me alone, please I´m just a bot ._."))
    
client = Client()

@client.tree.command(name = "test", description = "This is a test command")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(content = "test")

with open("config.json") as file:
    data = json.load(file)
    token = data["TOKEN"] 

client.run(token)