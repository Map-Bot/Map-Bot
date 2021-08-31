import files
import roles
import time
import discord
from discord.ext import commands, tasks
import os
import asyncio 
import sched
import datetime
import  aiocron
from keep_alive import keep_alive
from decorators import *
client = commands.Bot(command_prefix="%", intents=discord.Intents.all())

#Main should be used for the core, unchanging functions of the bot.


#Include hotswappable cogs code here


# https://tenor.com/view/wooo-yeah-baby-gif-18955985

async def wait_for(ctx, msg, reactions):
  for i in reactions:
    await msg.add_reaction(i)

  def check(reaction, user):
    return user == ctx.message.author and str(reaction.emoji) in reactions

  try:
    reaction, user = await client.wait_for('reaction_add', timeout=100.0, check=check)
    #await ctx.send(reaction)
    return str(reaction.emoji)
  except asyncio.TimeoutError:
    await ctx.send('The bot timed out, I tell you what')


@client.command()
async def setup(ctx):
  #Record each step of setup and save the configuration information and the exact step last completed in the config file of the game. 
  author = ctx.message.author
  embed = discord.Embed(color=0x1111ee)
  embed.add_field(name="Join or Host", value="Are you joining a current game or hosting a new one? ")
  msg = await ctx.send(embed=embed)
  reaction = await wait_for(ctx, msg, ["🇯","🇭"])

  embed.clear_fields()
  await msg.clear_reactions()
  if reaction == "🇯":
    embed.add_field(name="Join Game", value="What is the name of the game that you want to join?")
    mode = "join"
  elif reaction == "🇭":
    embed.add_field(name="Host Game", value="What is the name of the game that you want to host?")
    mode = "host"
  await msg.edit(embed= embed)
  def check(message):
    print(author)
    print(ctx.message.author)
    return author == message.author 
  message = await client.wait_for("message", timeout=100.0, check=check)
  game_check = files.check_game(message.content, ctx.guild.id) 
  if mode == "host":
    if game_check != None:
      if game_check == "has game":
        await ctx.send("This server already has a game going on")
      elif game_check == "name used":
        await ctx.send("Name already in use")
    else:
      embed.clear_fields()
      embed.add_field(name="Confirm Name", value=f"Confirm that you want the game to be named '{message.content}', as this cannot be changed later")
      await msg.edit(embed=embed)
      reaction = await wait_for(ctx, msg, ["🇾","🇳"])
      if reaction == "🇾":
        embed.clear_fields()
        await msg.clear_reactions()
        embed.add_field(name="Choose Game Type", value="Will this game be played using only one server or multiple?")
        await msg.edit(embed=embed)
        reaction = await wait_for(ctx, msg, ["1️⃣", "🔢"])
        await ctx.send("Game Created")
        if reaction == "🔢":
          await msg.delete()
          files.create_game(message.content, ctx.guild.id, "satellite")
        elif reaction == "1️⃣":
          await msg.delete()
          files.create_game(message.content, ctx.guild.id, "central")
        
        
      elif reaction == "🇳":
        await ctx.send("Game setup cancelled")
        return
      
      
  if mode == "join":
    if game_check == "name used":
      await ctx.send("Valid game")
    else:
      await ctx.send("This game does not exist")




@client.command()
async def join(ctx, faction):
  await ctx.send(f"Connor ain't finished, so you can't join {faction}")

@client.command()
async def test(ctx):
  def check(reaction, user):
    return user == ctx.message.author and str(reaction.emoji) == '👍'

  try:
    reaction, user = await client.wait_for('reaction_add', timeout=1.0, check=check)
  except asyncio.TimeoutError:
    await ctx.send('The bot timed out, I tell you what')

  print(reaction)

@client.command()
async def games(ctx):
  embed = discord.Embed(color=0x1111ee)
  for i in files.games():
    embed.add_field(name="**Game Name:**", value = i)
  await ctx.send(embed=embed)

@client.command()
@not_in_faction()
async def y(ctx):
  await ctx.message.delete()
  time.sleep(.1)
  await ctx.send("https://tenor.com/view/wooo-yeah-baby-gif-18955985")

@client.command()
async def end(ctx, name):
  files.end_game(name, str(ctx.guild.id))
  await ctx.send(f"Game '{name}' ended")

@aiocron.crontab('*/10 * * * *')
async def joe():
  channel= client.get_channel(830936450592800835)
  print(channel)
  #await channel.send("So true")
  print("joe done")


client.run(os.environ['api'])
asyncio.get_event_loop().run_forever()
'''  guild = client.get_channel(821486857367322629)
  print(guild)
  await discord.utils.get(guild.channels, name="test").send(f"Update #{users_who_claimed['update']} ")'''