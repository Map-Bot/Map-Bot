import typing
import os
import asyncio
import time

import discord
from discord.ext import commands
from discord import Client, Intents, Embed

import class_playground
#import roles
#from decorators import *
import r_test

client = commands.Bot(command_prefix="%", intents=discord.Intents.all())


# Main should be used for the core, unchanging functions of the bot.


# Include hotswappable cogs code here


# https://tenor.com/view/wooo-yeah-baby-gif-18955985


async def wait_for(
        ctx: commands.Context, msg: discord.Message,
        reactions: typing.List[typing.Union[str, discord.PartialEmoji]]) -> typing.Optional[str]:
    for i in reactions:
        await msg.add_reaction(i)

    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in reactions

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=100.0, check=check)
        return str(reaction.emoji)
    except asyncio.TimeoutError:
        await ctx.send('The bot timed out, I tell you what')
    return None


@client.command()
async def setup(ctx: commands.Context):
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
    game_check = r_test.load_from_id(ctx.guild.id)
        
    if mode == "host":
        if game_check != None:
            await ctx.send("This server already has a game going on")

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
                    game = class_playground.Game(message.content, ctx.guild.id, central=False)
                elif reaction == "1️⃣":
                    await msg.delete()
                    game = class_playground.Game(message.content, ctx.guild.id)


            elif reaction == "🇳":
                await ctx.send("Game setup cancelled")
                return

    if mode == "join":
        if game_check == "name used":
            await ctx.send("Valid game")
        else:
            await ctx.send("This game does not exist")


@client.command()
async def join(ctx: commands.Context, faction: str):
    game = r_test.load_from_id(ctx.guild.id)
    faction_obj = game.get_faction(faction)
    #check user isn't in faction
    print(faction_obj)
    if faction_obj != None:
        role = ctx.guild.get_role(faction_obj.roles[-1].central_id)
        await ctx.author.add_roles(role, reason = "Faction join")
        await ctx.send(f"You have sucessfully joined {faction}, you are now a {faction_obj.roles[-1].central_name}")
    else:
        await ctx.send(f"{faction} isn't a valid faction")


@client.command()
async def test(ctx: commands.Context):
    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) == '👍'
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=1.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('The bot timed out, I tell you what')
    print(reaction)


@client.command()
async def games(ctx: commands.Context):
    embed = discord.Embed(color=0x1111ee)
    for i in r_test.games():
        embed.add_field(name="**Game Name:**", value = i)
    await ctx.send(embed=embed)

@client.command()
async def maps(ctx):
    pass

@client.command()
async def map(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    image = game.map()
    if image != "No map":
        image.save("test.png")
        await ctx.send(file=discord.File("test.png"))
    else:
        await ctx.send("No map found for current game. Try using %add_map first")

#@client.command()
async def add_map(ctx, name):
    game = r_test.load_from_id(ctx.guild.id)
    await ctx.send(game.add_map(name))

@client.command()
#@not_in_faction()
async def y(ctx: commands.Context):
    await ctx.message.delete()
    time.sleep(.05)
    await ctx.send("https://tenor.com/view/wooo-yeah-baby-gif-18955985")

@client.command()
async def claim(ctx, id):
    game = r_test.load_from_id(ctx.guild.id)
    done = 0
    #game.create_faction("Faction 1")
    for i in ctx.author.roles:
        if game.get_faction(i.name) != None:
            done = 1
            await ctx.send(game.edit_province(id, game.get_faction(i.name)))

    
    image = game.map()

    image.save("test.png")
    if done == 1:
        await ctx.send(file=discord.File("test.png"))


@client.command()
async def update_roles(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    print(game.server_id)
    edited = []
    role_names = [i.name for i in ctx.guild.roles]
    for i in game.factions:
        for j in i.roles:
            if game.server_id == ctx.guild.id:
                if j.central_id == 0 and j.central_name not in role_names:
                    edited.append(j.central_name)
                    role = await ctx.guild.create_role(name=j.central_name, color=discord.Color.from_rgb(i.colors[0],i.colors[1],i.colors[2]))
                    j.central_id = role.id
                elif j.central_id != 0:
                    j.central_name = ctx.guild.get_role(j.central_id).name
                    print(j.central_name)
            elif i.server_id == ctx.guild.id:
                if j.satellite_id == 0 and j.satellite_name not in role_names:
                    edited.append(j.central_name)
                    role = await ctx.guild.create_role(name=j.central_name, color=discord.Color.from_rgb(i.colors[0],i.colors[1],i.colors[2]))
                    j.central_id = role.id
                elif j.central_id != 0:
                    j.central_name = ctx.guild.get_role(j.central_id).name
                    print(j.central_name)
    game.save()
    await ctx.send(f"Roles updated: {', '.join(edited)}")

@client.command()
async def newfac(ctx, name):
    game = r_test.load_from_id(ctx.guild.id)
    await ctx.send(game.create_faction(name))
    role = await ctx.guild.create_role(name=name, color=discord.Color.from_rgb(game.factions[-1].colors[0],game.factions[-1].colors[1],game.factions[-1].colors[2]))
    
    await ctx.author.add_roles(role, reason = "Faction creation")
    await update_roles(ctx)

@client.command()
async def factions(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    await ctx.send(game.faction_names())

@client.command()
async def clearfacs(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    for i in game.factions:
        for j in i.roles:
            if j.central_id != 0:
                try:
                    await ctx.guild.get_role(j.central_id).delete()
                except:
                    print("Role deletion error")
                    print(j.name)
                    print(j.central_id)
    game.factions = []
    game.save()
    await ctx.send("Factions sucessfully cleared")

@client.command()
async def myfac(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    for i in ctx.author.roles:
        if game.get_faction(i.name) != None:
            await ctx.send(i.name)
            
@client.command()
async def end(ctx: commands.Context, name: str):
    files.end_game(name, str(ctx.guild.id))
    await ctx.send(f"Game '{name}' ended")


client.run(os.environ['api'])
asyncio.get_event_loop().run_forever()