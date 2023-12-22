import discord
import json
import aiosqlite
from discord.ext import commands
from discord import app_commands

intents = discord.Intents().all()
client = commands.Bot(command_prefix = commands.when_mentioned_or("~"), intents = intents)

@client.event
async def on_ready():
    print("Bot is online! <3")
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER , guild INTEGER)")
        await db.commit()

@client.tree.command(name = "test", description = "This is a test command")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(content = "test")

@client.tree.command(name = "add_user", description = "Adds a user to the db")
async def add_user(interaction: discord.Interaction, member: discord.Member):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT id FROM users WHERE id = ? AND guild = ?", (member.id, interaction.guild.id,))
            data = await cursor.fetchone()
            if data:
                await cursor.execute("UPDATE users SET id = ? WHERE guild = ?", (member.id, interaction.guild.id,))
                await interaction.response.send_message(content = f"Member **{member.mention}** has been updated in the db")
            else:
                await cursor.execute("INSERT INTO users (id, guild) VALUES (?, ?)", (member.id, interaction.guild.id,))
                await interaction.response.send_message(content = f"Member **{member.mention}** has been updated in the db")
        await db.commit()

@client.tree.command(name = "remove_user", description = "Removes a user to the db")
async def remove_user(interaction: discord.Interaction, member: discord.Member):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT id FROM users WHERE guild = ?", (interaction.guild.id,))
            data = await cursor.fetchone()
            if data:
                await cursor.execute("DELETE FROM users WHERE id = ? AND guild = ?", (member.id, interaction.guild.id,))
                await interaction.response.send_message(content = f"Member **{member.mention}** has been removed from the db")
        await db.commit()


with open("config.json") as file:
    data = json.load(file)
    token = data["TOKEN"] 

client.run(token)