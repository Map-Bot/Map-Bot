import os
import asyncio
import time
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord import Client, Intents, Embed
from discord_slash import SlashCommand, SlashContext
from discord_slash.error import CheckFailure
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component, create_select, create_select_option
from discord_slash.model import ButtonStyle
import class_playground
import aiocron
from decorators import *
import r_test
import multiprocessing as mp

print(mp.cpu_count())
servers = [821486857367322624, 810657122932883477,902409343931154472]
schedules = {}
client = commands.Bot(command_prefix="%", intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)

# Main should be used for the core, unchanging functions of the bot.

print("Discord Main")
# Include hotswappable cogs code here


# https://tenor.com/view/wooo-yeah-baby-gif-18955985
async def map_update(id):
    games = r_test.games()
    for i in games:
        
        game = r_test.load_game_object(i)
        if game.server_id != id:
            continue
        guild = client.get_guild(game.server_id)


        for i in game.users:
            faction = game.get_faction(i.faction)
            if faction == None:
                continue
            for j in i.claims:
                game.edit_province(j, faction)
            i.claims = []
        game.current_claims = {}
        game.save()
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
            #channel = guild.get_channel(821486857367322629)
            image = game.redraw_map()
            print(image)
            if image != "No map":
                print("yes map")
                image.save("test.png")
                await channel.send("@everyone\nMap Update:",file=discord.File("test.png"))
            else:
                print("no map")
                continue
        except:
            print("Get channel error")
        print("Update complete!")

def check_update(game):
    if schedules.get(game.name) == None:
        print("adding scheduler")
        param=game.server_id
        async def filler():
            return await map_update(param)
        print(game.schedule)
        schedules[game.name] = aiocron.crontab(game.schedule, func = filler, start=True)
    


@dev()
@slash.slash(name="setup", description="Setup a game", guild_ids=servers)
async def slash_setup(ctx):
    await ctx.defer()
    author = ctx.author

    buttons1 = [
    create_button(style=ButtonStyle.blue, label="Join"),
    create_button(style=ButtonStyle.green, label="Host")
    ]

    action_row = create_actionrow(*buttons1)
    if r_test.load_from_id(ctx.guild.id) != None:
        await ctx.send("This server already has a game going on")
        return
    await ctx.send("Are you joining a current game or hosting a new one?",components=[action_row])
    button_ctx: ComponentContext = await wait_for_component(client, components=action_row)
    
    if button_ctx.component["label"] == "Host":
        await button_ctx.edit_origin(content="What is the name of the game that you want to host?", components=[])
    elif button_ctx.component["label"] == "Join":
        #await button_ctx.edit_origin(content="What is the name of the game that you want to join?", components=[])
        await button_ctx.edit_origin(content="This feature is not yet supported", components=[])
        return
    def check(message):
        return author == message.author
    message = await client.wait_for("message", timeout=60.0, check=check)
    buttons2 = [
        create_button(style=ButtonStyle.green, label=f"Yes, I want my game named '{message.content}'"),
        create_button(style=ButtonStyle.red, label="No, I want to cancel")
    ]
    action_row = create_actionrow(*buttons2)
    await ctx.send(content=f"Confirm that you want the game to be named '{message.content}', as this cannot be changed later", components=[action_row])
    button_ctx: ComponentContext = await wait_for_component(client, components=action_row)

    if button_ctx.component["label"] == f"Yes, I want my game named '{message.content}'":
        game = class_playground.Game(message.content, ctx.guild.id)
        await button_ctx.edit_origin(content=f"Game named: **{game.name}**", components=[])
        
    elif button_ctx.component["label"] == "No, I want to cancel":
        await button_ctx.edit_origin(content="Ok, cancelling", components=[])
        return

    select =create_select(options=create_select_option("TEM 3", value= "TEM3"))

    action_row = create_actionrow(create_select(options=[create_select_option("TEM 3", value= "TEM3")], placeholder="Choose your map", min_values=1, max_values=1))

    await ctx.send("What map would you like to use?", components = [action_row])
    
    select_ctx: ComponentContext = await wait_for_component(client, components=action_row)

    await select_ctx.edit_origin(content=f"Game **{game.name}** created", components=[])
    game.add_map(select_ctx.selected_options[0])
    await ctx.send("Added the selected map")

    

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

@slash_setup.error
async def setup_error(ctx, error):
    print(error)
    await ctx.send("You must be a dev to use this command")

@not_in_fac()
@slash.slash(name="join", description="Join the stated faction", guild_ids=servers)
async def join(ctx, faction):
    game = r_test.load_from_id(ctx.guild.id)
    user = game.get_user(ctx.author.id)
    faction_obj = game.get_faction(faction)
    #check user isn't in faction
    print(faction_obj)
    if faction_obj != None:
        role = ctx.guild.get_role(faction_obj.roles[-1].central_id)
        await ctx.author.add_roles(role, reason = "Faction join")
        user.faction = faction
        game.users[user.id].faction = faction
        faction_obj.users.append(user)
        await ctx.send(f"You have sucessfully joined the faction **{faction}**, you now have the role  '{faction_obj.roles[-1].central_name}'")
        game.save()
    else:
        await ctx.send(f"{faction} isn't a valid faction")

@join.error
async def join_error(ctx, error):
    await ctx.send("You must be factionless to use this command")

@client.command()
async def user(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    user = game.get_user(ctx.author.id)
    await ctx.send(user)


@in_fac()
@slash.slash(name="leave", description="Leave your current faction", guild_ids=servers)
async def leave(ctx):
    await ctx.defer()
    game = r_test.load_from_id(ctx.guild.id)
    user = game.get_user(ctx.author.id)
    empty = True
    faction = game.get_faction(user.faction)
    try:
        for i in game.users:
            if i.faction == user.faction and i != user:
                print("Two members")
                empty = False
    except:
        print("Get faction error")
    
    if empty:
        
        buttons2 = [
            create_button(style=ButtonStyle.green, label=f"Yes"),
            create_button(style=ButtonStyle.red, label="No")
        ]
        action_row = create_actionrow(*buttons2)
        await ctx.send(content=f"You are the last member of this faction, leaving will delete this faction, are you sure you want to leave?", components=[action_row])
        button_ctx: ComponentContext = await wait_for_component(client, components=action_row)

        if button_ctx.component["label"] == "Yes":
            await button_ctx.edit_origin(content=f"Deleting faction: **{faction.name}**", components=[])
            
        elif button_ctx.component["label"] == "No":
            await button_ctx.edit_origin(content="Ok, cancelling", components=[])
            return        

        for j in faction.roles:
            if j.central_id != 0:
                try:
                    await ctx.guild.get_role(j.central_id).delete()
                except:
                    print("Role deletion error")

        

    user.claims = []
    user.faction = ""
    for i in ctx.author.roles:
        if faction.name in i.name:
            await ctx.author.remove_roles(i)
                
    await ctx.send(f"You have successfully left faction: {faction.name}")
    game.factions.pop(faction.id-1)
    game.save()

@leave.error
async def leave_error(ctx: commands.Context, error:commands.CommandError):
    if isinstance(error, CheckFailure):
        await ctx.send("You must be in a faction to use this command")
    else:
        await ctx.send("An error occurred")
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


@slash.slash(name="games", description="Lists all of the games on the bot", guild_ids=servers)
async def games(ctx: commands.Context):
    embed = discord.Embed(color=0x1111ee)
    for i in r_test.games():
        embed.add_field(name="**Game Name:**", value = i)
    await ctx.send(embed=embed)


@client.command()
async def maps(ctx):
    pass


@slash.slash(name="map", description="Shows the latest map", guild_ids=servers)
async def map(ctx):
    print(test)
    await ctx.defer()
    game = r_test.load_from_id(ctx.guild.id)
    check_update(game)
    image = game.redraw_map()
    if image != "No map":
        image.save("test.png")
        await ctx.send(file=discord.File("test.png"))
        
    else:
        await ctx.send("No map found for current game. Try using /add_map first")

@slash.slash(name="add_map", description="Add the given map to the game", guild_ids=servers)
async def add_map(ctx, name):
    game = r_test.load_from_id(ctx.guild.id)
    await ctx.send(game.add_map(name))

@slash.slash(name="yes", description="WOOO!", guild_ids=servers)
async def y(ctx: commands.Context):
    await ctx.send("https://tenor.com/view/wooo-yeah-baby-gif-18955985")

@in_fac()
@slash.slash(name="claim", description="Claim the province with the given ID", guild_ids=servers)
async def claim(ctx, id):
    await ctx.defer()
    game = r_test.load_from_id(ctx.guild.id)
    user = game.get_user(ctx.author.id)
    check_update(game)
    done = 0
    faction = False
    for i in ctx.author.roles:
        if game.get_faction(i.name) != None:
            faction = i
            break
    if len(user.claims) > 1:
        await ctx.send("You have exceeded your maximum daily claims")
        return

    
    result = game.claim(id, game.get_faction(faction.name))
    await ctx.send(result)
    if result == "Sucessfully claimed":
        user.claims.append(id)
        image = game.redraw_map()
        image.save("test.png")
        await ctx.send(f"Successfully claimed province {id}",file=discord.File("test.png"))
    
    game.save()

@claim.error
async def claim_error(ctx: commands.Context, error):
    print(error)
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
                    role=ctx.guild.get_role(j.central_id)
                    j.central_name = role.name
                    await role.edit(color=discord.Color.from_rgb(i.colors[0],i.colors[1],i.colors[2]))
                    print("edited color")
                    print(i.colors)
                    print(j.central_name)
            elif i.server_id == ctx.guild.id:
                if j.satellite_id == 0 and j.satellite_name not in role_names:
                    edited.append(j.central_name)
                    role = await ctx.guild.create_role(name=j.central_name, color=discord.Color.from_rgb(i.colors[0],i.colors[1],i.colors[2]))
                    j.central_id = role.id
                elif j.central_id != 0:
                    role=ctx.guild.get_role(j.central_id)
                    j.central_name = role.name
                    print(j.central_name)
                    await role.edit(color=discord.Color.from_rgb(i.colors[0],i.colors[1],i.colors[2]))
    game.save()
    #await ctx.send(f"Roles updated: {', '.join(edited)}")

@not_in_fac()
#@has_permissions(manage_channels=True, manage_roles=True)
@slash.slash(name="newfac", description="Create a new faction with the provided name", guild_ids=servers)
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
    print("begin updating roles")
    await update_roles(ctx)
    print("finished updating roles")
    game = r_test.load_from_id(ctx.guild.id)
    print(game.factions[-1].roles)
    base_role = ctx.guild.get_role(game.factions[-1].roles[-1].central_id)
    print(game.factions[-1].roles)
    user.faction = name
    game.users[user.id] = user
    leader_role = ctx.guild.get_role(game.factions[-1].roles[0].central_id)
    await ctx.author.add_roles(base_role, reason = "Faction creation")
    await ctx.author.add_roles(leader_role, reason = "Faction creation")
    await ctx.send(f"Created faction: **{name}**")
    game.save()
   
@newfac.error
async def new_fac_error(ctx, error):
    print(f"Error: {error}end")
    print(type(error))
    if isinstance(error, commands.UnexpectedQuoteError) or isinstance(error, commands.InvalidEndOfQuotedStringError):
        await ctx.send("Invalid name, don't mess with quotes in the name")
    elif isinstance(error, CheckFailure):
        await ctx.send("You must be factionless to use this command")
    else:
        await ctx.send(f"An error occured, try a different name")


@slash.slash(name="factions", description="List the current factions of this game", guild_ids=servers)
async def factions(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    await ctx.send(str(game.faction_names()))
    
@dev()
@slash.slash(name="clearfacs", description="Clears all factions in game", guild_ids=servers)
async def clearfacs(ctx):
    await ctx.defer()
    game = r_test.load_from_id(ctx.guild.id)
    game.current_claims = {}
    for i in game.factions:
        for j in i.roles:
            if j.central_id != 0:
                try:
                    await ctx.guild.get_role(j.central_id).delete()
                except:
                    print("Role deletion error")
    game.factions = []
    game.save()
    print(game.current_claims)
    await ctx.send("Factions sucessfully cleared")

@clearfacs.error
async def clearfacs_error(ctx, error):
    await ctx.send("You must be a dev to use this command")

@slash.slash(name="myfac", description="Gives the name of the faction you are in", guild_ids=servers)
async def myfac(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    check_update(game)
    for i in ctx.author.roles:
        if game.get_faction(i.name) != None:
            await ctx.send(i.name)
            return
    await ctx.send("You are not in a faction. Use /join to join one")
    
@slash.slash(name="dorito", description="dorito", guild_ids=servers)
async def dorito(ctx):
    embed = discord.Embed(color=0xe69701)
    embed.title="the dorito"
    embed.set_image(url="https://media.discordapp.net/attachments/774773624396972042/776205016423464980/dorito.gif")
    await ctx.send(embed=embed)



@dev()
@slash.slash(name="update", description="*/1 * * * *", guild_ids=servers)
async def update(ctx, schedule):
    game = r_test.load_from_id(ctx.guild.id)
    param = "test"
    async def filler():
        return await map_update(param)
    game.schedule = schedule
    check_update(game)
    game.save()
    await ctx.send("done")

@update.error
async def update_error(ctx, error):
    await ctx.send("You must be a dev to use this command")

@dev()
@slash.slash(name="end_update", description="dev only", guild_ids=servers)
async def end_update(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    game.schedule = None
    schedules[game.name].stop()
    await ctx.send("All updates have been deleted")

@end_update.error
async def end_update_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("You must be a dev to use this command")
    else:
        await ctx.send("An error occurred")

@dev()
@slash.slash(name="delete_game", description="Permanently deletes the current game", guild_ids=servers)
async def delete_game(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    for i in game.factions:
        for j in i.roles:
            if j.central_id != 0:
                try:
                    await ctx.guild.get_role(j.central_id).delete()
                except:
                    print("Role deletion error")
    r_test.end_game(game.name)
    await ctx.send(f"Game **{game.name}** has been deleted")

@delete_game.error
async def delete_game_error(ctx, error):
    print(error)
    await ctx.send("You must be a dev to use this command")

@slash.slash(name="size", description="Returns size of the game object in bytes", guild_ids=servers)
async def size(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    await ctx.send(f"The game size is {round(game.game_size()/1000000, 2)} MB")

@slash.slash(name="current_claims", description="Shows the map of the claims made this udpate", guild_ids=servers)
async def current_claims(ctx):
    await ctx.defer()
    game = r_test.load_from_id(ctx.guild.id)
    image = game.current_claims_map()
    if image != "No map":
        image.save("test.png")
        await ctx.send(file=discord.File("test.png"))
        
    else:
        await ctx.send("No map found for current game. Try using /add_map first")

@in_fac()
@slash.slash(name="change_faction_color", description="Changes the faction color to the given RGB values", guild_ids=servers)
async def change_faction_color(ctx, color):
    await ctx.defer()
    game = r_test.load_from_id(ctx.guild.id)
    user = game.get_user(ctx.author.id)
    faction = game.get_faction(user.faction)
    leader = False
    for i in ctx.author.roles:
        if "Leader" in i.name:
            leader = True

    if user.rank == "Leader" or leader:
        await ctx.send("Warning, may be a little broken")
        colors = color.strip().split(",")
        if len(colors) != 3:
            await ctx.send("You need exactly three values (RGB) to change the color. Try something like **0, 0, 255")
            return
        for index, i in enumerate(colors):
            if not i.isdigit():
                await ctx.send("The RGB values must be numbers")
                return
            if int(i) > 254 or int(i) < 1:
                await ctx.send("The RGB values must be between 1 and 254")
            colors[index] = int(i)

        print(colors)
        print(faction.roles[0].colors)
        for i in faction.roles:
            i.colors = colors
        faction.colors = colors

        game.factions[faction.id-1] = faction
        game.save()
        await update_roles(ctx)
        
        await ctx.send("Faction color updated")
        
    else:
        await ctx.send("You must be the leader of your faction to use this command")

@change_faction_color.error
async def change_faction_color_error(ctx: commands.Context, error):
    print(error)
    if isinstance(error, CheckFailure):
        await ctx.send("You must be in a faction to use this command")

@slash.slash(name="id_map", description="Shows the id map for the current map", guild_ids=servers)
async def id_map(ctx):
    await ctx.send("https://media.discordapp.net/attachments/878093499399041095/884572546673029151/Extremist_Map_3_Province_Map_Water_Connection_.png?")
client.run(os.environ['api'])
asyncio.get_event_loop().run_forever()