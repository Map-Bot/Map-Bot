import os
import asyncio
import time
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord import Client, Intents, Embed
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from discord_slash.model import ButtonStyle
import class_playground
import aiocron
#import roles
from decorators import *
import r_test


client = commands.Bot(command_prefix="%", intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)

# Main should be used for the core, unchanging functions of the bot.

print("Discord Main")
# Include hotswappable cogs code here


# https://tenor.com/view/wooo-yeah-baby-gif-18955985

@slash.slash(name="setup", description="Setup a game", guild_ids=[821486857367322624])
async def slash_setup(ctx):
    author = ctx.author

    buttons1 = [
    create_button(style=ButtonStyle.blue, label="Join"),
    create_button(style=ButtonStyle.green, label="Host")
    ]

    action_row = create_actionrow(*buttons1)
    await ctx.send("Are you joining a current game or hosting a new one?",components=[action_row])
    button_ctx: ComponentContext = await wait_for_component(client, components=action_row)
    
    if button_ctx.component["label"] == "Host":
        await button_ctx.edit_origin(content="What is the name of the game that you want to host?", components=[])
    elif button_ctx.component["label"] == "Join":
        await button_ctx.edit_origin(content="What is the name of the game that you want to join?", components=[])

    
    def check(message):
        return author == message.author
    message = await client.wait_for("message", timeout=10.0, check=check)
    buttons2 = [
        create_button(style=ButtonStyle.green, label=f"Yes, I want my game named '{message.content}'"),
        create_button(style=ButtonStyle.red, label="No, I want to cancel")
    ]
    action_row = create_actionrow(*buttons2)
    await ctx.send(content=f"Confirm that you want the game to be named '{message.content}', as this cannot be changed later", components=[action_row])
    button_ctx: ComponentContext = await wait_for_component(client, components=action_row)
    if button_ctx.component["label"] == f"Yes, I want my faction named '{message.content}'":
        await button_ctx.edit_origin(content="Game created", components=[])
    elif button_ctx.component["label"] == "No, I want to cancel":
        await button_ctx.edit_origin(content="Ok, cancelling", components=[])


async def wait_for(ctx,msg, reactions):
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


@commands.command
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

#@not_in_fac()
@slash.slash(name="join", description="Join the stated faction", guild_ids=[821486857367322624])
async def join(ctx, faction):
    game = r_test.load_from_id(ctx.guild.id)
    user = game.get_user(ctx.author.id)
    faction_obj = game.get_faction(faction)
    #check user isn't in faction
    print(faction_obj)
    if faction_obj != None:
        role = ctx.guild.get_role(faction_obj.roles[-1].central_id)
        await ctx.author.add_roles(role, reason = "Faction join")
        faction_obj.users.append(user)
        await ctx.send(f"You have sucessfully joined the faction **{faction}**, you now have the role  '{faction_obj.roles[-1].central_name}'")
    else:
        await ctx.send(f"{faction} isn't a valid faction")


@client.command()
async def user(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    user = game.get_user(ctx.author.id)
    await ctx.send(user)


@in_fac()
@slash.slash(name="leave", description="Leave your current faction", guild_ids=[821486857367322624])
async def leave(ctx):
    await ctx.defer()
    game = r_test.load_from_id(ctx.guild.id)
    faction = get_faction(ctx)
    if faction:
        for i in ctx.author.roles:
            if faction.name in i.name:
                await ctx.author.remove_roles(i)
                await ctx.send(f"You have successfully left faction: {faction.name}")

@leave.error
async def leave_error(ctx: commands.Context, error:commands.CommandError):
    await ctx.send("You must be in a faction to use this command")

    print(error)



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


@slash.slash(name="map", description="Shows the latest map", guild_ids=[821486857367322624])
async def map(ctx):
    print(test)
    await ctx.defer()
    game = r_test.load_from_id(ctx.guild.id)
    image = game.map()
    if image != "No map":
        image.save("test.png")
        await ctx.send(file=discord.File("test.png"))
    else:
        await ctx.send("No map found for current game. Try using %add_map first")

@slash.slash(name="add_map", description="Add the given map to the game", guild_ids=[821486857367322624])
async def add_map(ctx, name):
    game = r_test.load_from_id(ctx.guild.id)
    await ctx.send(game.add_map(name))

@slash.slash(name="yes", description="WOOO!", guild_ids=[821486857367322624])
#@not_in_faction()
async def y(ctx: commands.Context):
    await ctx.send("https://tenor.com/view/wooo-yeah-baby-gif-18955985")

@in_fac()
@slash.slash(name="claim", description="Claim the province with the given ID", guild_ids=[821486857367322624])
async def claim(ctx, id):
    await ctx.defer()
    game = r_test.load_from_id(ctx.guild.id)
    user = game.get_user(ctx.author.id)
    done = 0
    faction = False
    for i in ctx.author.roles:
        if game.get_faction(i.name) != None:
            faction = i
            break
    if len(user.claims) > 100:
        await ctx.send("You have exceeded your maximum daily claims")
        return

    
    result = game.edit_province(id, game.get_faction(faction.name))
    await ctx.send(result)
    if result == "Sucessfully claimed":
        user.claims.append(id)
        image = game.map()
        image.save("test.png")
        await ctx.send(file=discord.File("test.png"))
    
    game.save()
@claim.error
async def claim_error(ctx: commands.Context, error):
    await ctx.send("You must be in a faction to use this command")

#@client.command()
async def update_roles(ctx):
    game = r_test.load_from_id(ctx.guild.id)
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
    #await ctx.send(f"Roles updated: {', '.join(edited)}")

@not_in_fac()
#@has_permissions(manage_channels=True, manage_roles=True)
@slash.slash(name="newfac", description="Create a new faction with the provided name", guild_ids=[821486857367322624])
async def newfac(ctx, name):
    #Add config option later for restricting certain characters like : 
    game = r_test.load_from_id(ctx.guild.id)
    user = game.get_user(ctx.author.id)
    await ctx.defer()

    if len(name) > 20 or len(name) < 1:
        await ctx.send("Faction name must be less than or equal to 20 characters and greater than zero")
        return
    forbidden_characters = ["%", "Admin", "/","\'","\"","."]
    for i in forbidden_characters:
        if i.lower() in name.lower():
            await ctx.send(f"Invalid character: '{i}'")
            return
    role_names = []
    for i in ctx.guild.roles:
        role_names.append(i.name)

    if name in role_names:
        await ctx.send("Role name already exists, try a different name")
        return
    if game.create_faction(name) == "Faction name already exists":
        await ctx.send("Faction name already exists")
        return
    await update_roles(ctx)
    game = r_test.load_from_id(ctx.guild.id)
    role = ctx.guild.get_role(game.factions[-1].roles[-1].central_id)
    await ctx.author.add_roles(role, reason = "Faction creation")
    
    await ctx.send("Done")
   
@newfac.error
async def new_fac_error(ctx: commands.Context, error: commands.CommandError):
    print(error)
    if isinstance(error, commands.UnexpectedQuoteError) or isinstance(error, commands.InvalidEndOfQuotedStringError):
        await ctx.send("Invalid name, don't mess with quotes in the name")
    elif isinstance(error, commands.CheckFailure):
        print("In faction")
    else:
        await ctx.send(f"An error occured, try a different name")


@slash.slash(name="factions", description="List the current factions of this game", guild_ids=[821486857367322624])
async def factions(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    await ctx.send(str(game.faction_names()))
    

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
    game.factions = []
    game.save()
    await ctx.send("Factions sucessfully cleared")

@slash.slash(name="myfac", description="Gives the name of the faction you are in", guild_ids=[821486857367322624])
async def myfac(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    for i in ctx.author.roles:
        if game.get_faction(i.name) != None:
            await ctx.send(i.name)
            return
    await ctx.send("You are not in a faction. Use /join to join one")
    
@slash.slash(name="dorito", description="dorito", guild_ids=[821486857367322624])
async def dorito(ctx):
    embed = discord.Embed(color=0xe69701)
    embed.title="the dorito"
    embed.set_image(url="https://media.discordapp.net/attachments/774773624396972042/776205016423464980/dorito.gif")
    await ctx.send(embed=embed)

async def map_update(test):
    games = r_test.games()
    for i in games:
        game = r_test.load_game_object(i)
        guild = client.get_guild(game.server_id)
        image = game.map()
        if image != "No map":
            image.save("test.png")
        else:
            print("no map")
            continue
        try:
            channel_id = 0
            for i in guild.channels:
                if "map" == i.name:
                    channel_id = i.id
            if channel_id == 0:
                overwrites = {guild.default_role: discord.PermissionOverwrite(send_messages=False),guild.me: discord.PermissionOverwrite(send_messages=True)}
                map_channel = await guild.create_text_channel("map", overwrites=overwrites)
                channel_id = map_channel.id
            channel = guild.get_channel(channel_id)

            await channel.send(file=discord.File("test.png"))
        except:
            print("Get channel error")
        print(game.server_id)


@slash.slash(name="update", description="a", guild_ids=[821486857367322624])
async def update(ctx , param):
    async def fill():
        return await map_update(param)
    cron = aiocron.crontab('*/10 * * * *', func = fill, start=True)
    await ctx.send("done")

client.run(os.environ['api'])
asyncio.get_event_loop().run_forever()