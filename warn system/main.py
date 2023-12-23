import discord
import json
import aiosqlite
import asyncio
import datetime
from discord.ext import commands
from discord import app_commands

intents = discord.Intents().all()
client = commands.Bot(command_prefix = commands.when_mentioned_or("~"), intents = intents)

@client.event
async def on_ready():
    print("Bot is online! <3")
    await client.change_presence(activity = discord.Game("Leave me alone, please I´m just a bot ._."))
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    client.db = await aiosqlite.connect("warns.db")
    await asyncio.sleep(3)
    async with client.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS warns (user INTEGER, reason TEXT, time INTEGER, guild INTEGER)")
    await client.db.commit()

async def addwarn(interaction, reason, user):
    async with client.db.cursor() as cursor:
        await cursor.execute("INSERT INTO warns (user, reason, time, guild) VALUES (?, ?, ?, ?)", (user.id, reason, int(datetime.datetime.now().timestamp()), interaction.guild.id))
    await client.db.commit()

@client.tree.command(name = "test", description = "This is a test command")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(content = "test")

@client.tree.command(name = "warn", description = "Warns a member")
@commands.has_permissions(manage_messages = True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    await addwarn(interaction, reason, member)

    embed = discord.Embed(
        title = "Warn",
        description = f"Member {member.mention} has been warned.\nReason: *{reason}*",
        color = discord.Color.red(),
        timestamp = datetime.datetime.utcnow()
    )
    await interaction.response.send_message(embed = embed)

@client.tree.command(name = "remove_warn", description = "Removes a members warning")
@commands.has_permissions(manage_guild = True)
async def remove_warn(interaction: discord.Interaction, member: discord.Member):
    async with client.db.cursor() as cursor:
        await cursor.execute("SELECT reason FROM warns WHERE user = ? AND guild = ?", (member.id, interaction.guild.id))
        data = await cursor.fetchone()
        if data:
            await cursor.execute("DELETE FROM warns WHERE user = ? AND guild = ?", (member.id, interaction.guild.id))

            embed = discord.Embed(
            title = "Warn remove",
            description = f"Member´s {member.mention} warning has been deleted.",
            color = discord.Color.red(),
            timestamp = datetime.datetime.utcnow()
            )
            await interaction.response.send_message(embed = embed)

        else:
            embed2 = discord.Embed(
            title = "Warn remove",
            description = f"No warnings found!",
            color = discord.Color.red(),
            timestamp = datetime.datetime.utcnow()
            )
            await interaction.response.send_message(embed = embed2)
            
    await client.db.commit()

@client.tree.command(name = "warns", description = "Veiws a members warning")
@commands.has_permissions(manage_messages = True)
async def warns(interaction: discord.Interaction, member: discord.Member):
    async with client.db.cursor() as cursor:
        await cursor.execute("SELECT reason, time FROM warns WHERE user = ? AND guild = ?", (member.id, interaction.guild.id))
        data = await cursor.fetchall()
        if data:
            embed = discord.Embed(
                title = f"{member.name}´s warnings",
                description = f"Here are all warnings of member {member.mention}",
                color = discord.Color.blue(),
                timestamp = datetime.datetime.utcnow()
            )
            warnnum = 0
            for table in data:
                warnnum += 1
                embed.add_field(
                    name = f"Warning {warnnum}",
                    value = f"Reason: {table[0]}\nDate issued: <t:{int(table[1])}:F>",
                )
            await interaction.response.send_message(embed = embed)
        else:
            embed2 = discord.Embed(
                title = f"{member.name}´s warnings",
                description = f"No warnings found!",
                color = discord.Color.blue(),
                timestamp = datetime.datetime.utcnow()
            )
            await interaction.response.send_message(embed = embed2)
    await client.db.commit()

with open("config.json") as file:
    data = json.load(file)
    token = data["TOKEN"] 

client.run(token)