from class_playground import Game
import discord
import asyncio
import os
import r_test
import io
from discord import Client, Intents, Embed
from discord_slash import SlashCommand, SlashContext

bot = Client(intents=Intents.default())
slash = SlashCommand(bot)

@slash.slash(name="test")
async def test(ctx: SlashContext):
    embed = Embed(title="Embed Test")
    await ctx.send(embed=embed)

#Create game command (make sure to connect to server)



#Create faction command. Take in the name as an input



#Claim command. Take in the province id and faction. Make sure faction exists. Edit selected province to the faction id.


bot.run(os.environ['api'])