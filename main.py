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
import random
from PIL import Image
import io
import base64
import image
import logging
Log_Format = "%(levelname)s %(asctime)s - %(message)s"
os.environ['TZ'] = 'PST8PDT'
time.tzset()
logging.basicConfig(filename = "logfile.log", filemode = "w", format = Log_Format, level = logging.INFO)
log = logging.getLogger("my-logger")
#print(mp.cpu_count())
servers = [828422029618446399,810657122932883477,935758410090160159]
exempt = [339251879273955330,740630812315090984,811024803292905532]
schedules = {}
client = commands.Bot(command_prefix="%", intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)

# Main should be used for the core, unchanging functions of the bot.
print("Discord Main")
def user_log(game, user, command_name, command_info):
	log.info(f"\nCOMMAND NAME: {command_name}\nCOMMAND INFO: {command_info}\nUSER INFO:\nUser Object: {user} - User Object Name: {user.name} - User Faction: {user.faction} - User Actions: {user.actions}")
	if isinstance(user.faction, class_playground.Faction):
		pass
		#this little shit causes so many problems
		#log.info(f"User Faction ID: {user.faction.id} ")
async def fix_shit(game, discord_user):
	print("factions---------------------")
	print(game.factions)
	for i in discord_user.roles:
		result = game.get_faction(i.name)
		if result:
			game.users[discord_user.id].faction = result
			game.users[discord_user.id].name = discord_user.name
			game.save()
# Include hotswappable cogs code here
#
def error_embed(content, title="Attention!"):
	embed = discord.Embed(title=f"**{title}**", color=0xf1ad02,description=content)
	embed.set_thumbnail(url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.freepngimg.com%2Fthumb%2Femoji%2F81186-triangle-danger-text-area-sign-messaging-emoji.png&f=1&nofb=1")
	return embed
def success_embed(content, title="Success!"):
	embed = discord.Embed(title=f"**{title}**", color=0xaadaff,description=content)
	embed.set_thumbnail(url="http://clipart-library.com/images_k/check-mark-png-transparent/check-mark-png-transparent-12.png")
	return embed
# https://tenor.com/view/wooo-yeah-baby-gif-18955985
async def map_update(id):
	log.info("Updating the map")
	print("UPDATING MAP")
	games = r_test.games()
	for game_it in games:
		game = r_test.load_game_object(game_it)
		log.debug(f"GAME JSON: {game.game_json}")
		if game.server_id != id:
			continue
		guild = client.get_guild(game.server_id)
		#log.info(f"Game User List: {game.users.values()}")
		log.debug(f"USER VALUES: {game.users}")
		for temp in game.users:
			i = game.users[temp]
			print(temp)
			print(i)
			print(i.faction)
			if isinstance(i.faction, class_playground.Faction):
				faction = i.faction
			else:
				faction = game.get_faction(name=i.faction)
			if faction == None:
				continue
			log.info(f"Claim list for user {i.name}: {i.claims}")
			#log.info(f"User Object Info: {dir(i)}")
			for j in i.claims:
				print("redraw")
				log.info(f"-----EDITED PROVINCE: {j} NEW OWNER: {faction.name}------")
				log.debug(f"RESULT OF PROVINCE EDIT: {game.edit_province(j, faction)}")

			i.claims = []
			i.actions = 0
		game.current_claims = {}
		game.save()
		
		try:
			battle_channel_id = None
			channel_id = None
			for i in guild.channels:
				if "map" == i.name:
					channel_id = i.id
				if "battle-log" ==i.name:
					battle_channel_id = i.id
			if channel_id == None:
				overwrites = {
				    guild.default_role:
				    discord.PermissionOverwrite(send_messages=False),
				    guild.me:
				    discord.PermissionOverwrite(send_messages=True)
				}
				map_channel = await guild.create_text_channel(
				    "map", overwrites=overwrites)
				channel_id = map_channel.id
			if battle_channel_id == None:
				overwrites = {
				    guild.default_role:
				    discord.PermissionOverwrite(send_messages=False),
				    guild.me:
				    discord.PermissionOverwrite(send_messages=True)
				}
				battle_channel = await guild.create_text_channel(
				    "battle-log", overwrites=overwrites)
				battle_channel_id = battle_channel.id				
			channel = guild.get_channel(channel_id)
			
			map_result = game.redraw_map()
			if map_result != "No map":
				print("yes map")
				map_result.save("test.png")
				await channel.send(f"@everyone\nMap Update\nClaims: {game_it.action_limit}",
				                   file=discord.File("test.png"))
			else:
				print("no map")
				continue
		except Exception as e:
			print(e)
			print("Get channel error")

		print("getting battle channel")
		battle_channel = guild.get_channel(battle_channel_id)
		print(battle_channel.name)
		temp_keys = list(game.attacks.keys())
		for attack in temp_keys:
			print(attack)
			attack_info = game.attacks.get(attack)
			attack_dice = []
			defense_dice = []
			for i in range(len(attack_info["attackers"])):
				attack_dice.append(random.randint(1,6))
			for i in range(len(attack_info["defenders"])):
				defense_dice.append(random.randint(1,6))
			attack_dice.sort(reverse=True)
			defense_dice.sort(reverse=True)
		
			embed = discord.Embed(title="**BATTLE RESULTS**", color = 0x5ac30a)
			embed.add_field(name="***Defender Victory!***",value=f"The attackers were repealed in a glorious defense of province {attack}!")
			embed.set_thumbnail(url="https://cdn2.iconfinder.com/data/icons/rpg-fantasy-game-skill-ui/512/game_skill_ui_guard_shield_broken_sword-512.png")
			if sum(defense_dice) < sum(attack_dice):
				game.game_json[attack] = game.game_json[attack_info["attacking_province"]]
				win = True
				embed = discord.Embed(title="**BATTLE RESULTS**", color = 0xf92424)
				embed.set_thumbnail(url="https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fclipart-library.com%2Fimg1%2F1063584.png&f=1&nofb=1")
				embed.add_field(name="***Attacker Victory!***", value=f"A righteous victory over the enemy was achieved at province {attack}!")
			embed.add_field(name="Attack Dice", value=f"Attack Dice Rolls: `{', '.join(str(i) for i in attack_dice)}`\nSum Total: {sum(attack_dice)}", inline=False)
			embed.add_field(name="Defense Dice", value=f"Defense Dice Rolls: `{', '.join(str(i) for i in defense_dice)}`\nSum Total: {sum(defense_dice)}", inline=False)
			base_coords = r_test.map_json(game.map_name)[f"l{attack}"]["coordinates"][0]
			base_coords = eval(base_coords)
			print(base_coords)
			img = game.map()
			image.snapshot(img, base_coords)
			embed.set_image(url="attachment://snapshot.png")
			print("sending")
			await battle_channel.send(embed=embed, file=discord.File("snapshot.png"))
			game.attacks.pop(attack)
		game.save()
		print("Update complete!")


def check_update(game):
	print("CHECKING UPDATE")
	if schedules.get(game.name) == None:
		print("adding scheduler")
		param = game.server_id

		async def filler():
			return await map_update(param)

		print(game.schedule)
		schedules[game.name] = aiocron.crontab(game.schedule,
		                                       func=filler,
		                                       start=True)


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
	await ctx.send("Are you joining a current game or hosting a new one?",
	               components=[action_row])
	button_ctx: ComponentContext = await wait_for_component(
	    client, components=action_row)

	if button_ctx.component["label"] == "Host":
		await button_ctx.edit_origin(
		    content="What is the name of the game that you want to host?",
		    components=[])
	elif button_ctx.component["label"] == "Join":
		#await button_ctx.edit_origin(content="What is the name of the game that you want to join?", components=[])
		await button_ctx.edit_origin(
		    content="This feature is not yet supported", components=[])
		return

	def check(message):
		return author == message.author

	message = await client.wait_for("message", timeout=60.0, check=check)
	buttons2 = [
	    create_button(style=ButtonStyle.green,
	                  label=f"Yes, I want my game named '{message.content}'"),
	    create_button(style=ButtonStyle.red, label="No, I want to cancel")
	]
	action_row = create_actionrow(*buttons2)
	await ctx.send(
	    content=
	    f"Confirm that you want the game to be named '{message.content}', as this cannot be changed later",
	    components=[action_row])
	button_ctx: ComponentContext = await wait_for_component(
	    client, components=action_row)

	if button_ctx.component[
	    "label"] == f"Yes, I want my game named '{message.content}'":
		game = class_playground.Game(message.content, ctx.guild.id)
		await button_ctx.edit_origin(content=f"Game named: **{game.name}**",
		                             components=[])

	elif button_ctx.component["label"] == "No, I want to cancel":
		await button_ctx.edit_origin(content="Ok, cancelling", components=[])
		return

	select = create_select(options=create_select_option("TEM 3", value="TEM3"))

	action_row = create_actionrow(
	    create_select(options=[create_select_option("TEM 3", value="TEM3")],
	                  placeholder="Choose your map",
	                  min_values=1,
	                  max_values=1))

	await ctx.send("What map would you like to use?", components=[action_row])

	select_ctx: ComponentContext = await wait_for_component(
	    client, components=action_row)

	await select_ctx.edit_origin(content=f"Game **{game.name}** created",
	                             components=[])
	game.add_map(select_ctx.selected_options[0])
	await ctx.send("Added the selected map")


async def wait_for(ctx, msg, reactions):
	for i in reactions:
		await msg.add_reaction(i)

	def check(reaction, user):
		return user == ctx.message.author and str(reaction.emoji) in reactions

	try:
		reaction, user = await client.wait_for('reaction_add',
		                                       timeout=100.0,
		                                       check=check)
		return str(reaction.emoji)
	except asyncio.TimeoutError:
		await ctx.send('The bot timed out, I tell you what')
	return None


@commands.command
async def setup(ctx: commands.Context):
	#Record each step of setup and save the configuration information and the exact step last completed in the config file of the game.
	author = ctx.message.author
	embed = discord.Embed(color=0x1111ee)
	embed.add_field(
	    name="Join or Host",
	    value="Are you joining a current game or hosting a new one? ")
	msg = await ctx.send(embed=embed)
	reaction = await wait_for(ctx, msg, ["🇯", "🇭"])

	embed.clear_fields()
	await msg.clear_reactions()
	if reaction == "🇯":
		embed.add_field(
		    name="Join Game",
		    value="What is the name of the game that you want to join?")
		mode = "join"
	elif reaction == "🇭":
		embed.add_field(
		    name="Host Game",
		    value="What is the name of the game that you want to host?")
		mode = "host"
	await msg.edit(embed=embed)

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
			embed.add_field(
			    name="Confirm Name",
			    value=
			    f"Confirm that you want the game to be named '{message.content}', as this cannot be changed later"
			)
			await msg.edit(embed=embed)
			reaction = await wait_for(ctx, msg, ["🇾", "🇳"])
			if reaction == "🇾":
				embed.clear_fields()
				await msg.clear_reactions()
				embed.add_field(
				    name="Choose Game Type",
				    value=
				    "Will this game be played using only one server or multiple?"
				)
				await msg.edit(embed=embed)
				reaction = await wait_for(ctx, msg, ["1️⃣", "🔢"])
				await ctx.send("Game Created")
				if reaction == "🔢":
					await msg.delete()
					game = class_playground.Game(message.content,
					                             ctx.guild.id,
					                             central=False)
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
	await ctx.send(embed=error_embed("You must be a dev to use this command"))


@not_in_fac()
@slash.slash(name="Apply",
             description="Apply to the stated faction",
             guild_ids=servers)
async def join(ctx, faction):
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	faction_obj = game.get_faction(name=faction)
	#check user isn't in faction
	user_log(game, user, "apply", f"Target Faction Name: {faction} - Faction Object: {faction_obj}")

	if faction_obj != None:
		log.info(f"Target Faction Name: {faction_obj.name}")
		role = ctx.guild.get_role(faction_obj.roles[-1].central_id)
		await ctx.author.add_roles(role, reason="Faction join")
		user.faction = faction_obj
		game.users[user.id].faction = faction_obj
		game.users[user.id].rank = faction_obj.roles[-1].central_id
		faction_obj.users.append(user)
		await ctx.send(embed=success_embed(
		    f"You have sucessfully applied the faction **{faction}**, you now have the role  '{faction_obj.roles[-1].central_name}\n<@&{faction_obj.roles[2].central_id}>'"
		))
		game.save()
	else:
		await ctx.send(embed=error_embed(f"{faction} isn't a valid faction"))


@join.error
async def join_error(ctx, error):
	log.error(error)
	await ctx.send(embed=error_embed("You must be factionless to use this command"))


@client.command()
async def user(ctx):
	print(ctx.author)
	print(ctx.author.id)
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	await ctx.send(user)


@in_fac()
@slash.slash(name="leave",
             description="Leave your current faction",
             guild_ids=servers)
async def leave(ctx):
	await ctx.defer()
	game = r_test.load_from_id(ctx.guild.id)

	user = game.users[ctx.author.id]
	user_log(game, user, "leave", f"N/A")
	empty = True
	faction = user.faction
	if not isinstance(faction, class_playground.Faction):
		faction = game.get_faction(name=faction)
	print(user.faction)
	print(faction)
	mems = 0
	for i in faction.roles:
		log.info(f"Members list for role name: {ctx.guild.get_role(i.central_id).name}\n{ctx.guild.get_role(i.central_id).members}")
		mems += len(ctx.guild.get_role(i.central_id).members)
	if mems > 2:
		print(f"Members: {mems}")
		log.info(f"Members left in faction: {mems}")
		empty = False
	#try:
	for i in list(game.users.values()):
		print(i.faction)
		if isinstance(i.faction, class_playground.Faction):
			print(i.faction.name)
			if i.faction.name == user.faction and i != user:
				print("Two members")
				empty = False
	#except:
		#print("Get faction error")

	if empty:
		buttons2 = [
		    create_button(style=ButtonStyle.green, label=f"Yes"),
		    create_button(style=ButtonStyle.red, label="No")
		]
		action_row = create_actionrow(*buttons2)
		await ctx.send(
		    content=
		    f"You are the last member of this faction, leaving will delete this faction, are you sure you want to leave?",
		    components=[action_row])
		button_ctx: ComponentContext = await wait_for_component(
		    client, components=action_row)
		if button_ctx.component["label"] == "Yes":
			await button_ctx.edit_origin(
			    content=f"Deleting faction: **{faction.name}**", components=[])

		elif button_ctx.component["label"] == "No":
			await button_ctx.edit_origin(content="Ok, cancelling",
			                             components=[])
			return

		for j in faction.roles:
			if j.central_id != 0:
				try:
					await ctx.guild.get_role(j.central_id).delete()
				except:
					print("Role deletion error")
		for i in list(game.game_json.keys()):
			if game.game_json[i] == faction.id:
				game.game_json[i] = 0
		for i in list(game.current_claims.keys()):
			if game.current_claims[i] == faction.id:
				game.current_claims.pop(i)
		game.factions.pop(faction.id)
	central_role_names = [i.central_name for i in faction.roles]
	satellite_role_names = [i.satellite_name for i in faction.roles]
	total_names = central_role_names + satellite_role_names
	print(f"Role Names: {total_names}")
	user.claims = []
	user.faction = ""
	for i in ctx.author.roles:
		if i.name in total_names:
			print(f"Removing Role: {i.name}")
			await ctx.author.remove_roles(i)
			print("Done removing")
	print("sending message")
	await ctx.send(embed=success_embed(f"You have successfully left faction: {faction.name}"))
	print("Done")
	game.save()



@leave.error
async def leave_error(ctx: commands.Context, error: commands.CommandError):
	if isinstance(error, CheckFailure):
		await ctx.send(embed=error_embed("You must be in a faction to use this command"))
	else:
		await ctx.send(embed=error_embed("An error occurred"))
	print(error)


@client.command()
async def test(ctx: commands.Context):
	def check(reaction, user):
		return user == ctx.message.author and str(reaction.emoji) == '👍'

	try:
		reaction, user = await client.wait_for('reaction_add',
		                                       timeout=1.0,
		                                       check=check)
	except asyncio.TimeoutError:
		await ctx.send('The bot timed out, I tell you what')
	print(reaction)


@slash.slash(name="games",
             description="Lists all of the games on the bot",
             guild_ids=servers)
async def games(ctx: commands.Context):
	embed = discord.Embed(color=0x1111ee)
	for i in r_test.games():
		embed.add_field(name="**Game Name:**", value=i)
	await ctx.send(embed=embed)


@client.command()
async def maps(ctx):
	pass


@slash.slash(name="map", description="Shows the latest map", guild_ids=servers)
async def map(ctx):
	await ctx.defer()
	game = r_test.load_from_id(ctx.guild.id)
	#check_update(game)
	image = game.map()
	if image != "No map":
		image.save("test.png")
		await ctx.send(file=discord.File("test.png"))

	else:
		await ctx.send(
		    "No map found for current game. Try using /add_map first")


@slash.slash(name="add_map",
             description="Add the given map to the game",
             guild_ids=servers)
async def add_map(ctx, name):
	game = r_test.load_from_id(ctx.guild.id)
	await ctx.send(game.add_map(name))


@slash.slash(name="yes", description="WOOO!", guild_ids=servers)
async def y(ctx: commands.Context):
	await ctx.send("https://tenor.com/view/wooo-yeah-baby-gif-18955985")


@in_fac()
@slash.slash(name="claim",
             description="Claim the province with the given ID",
             guild_ids=servers)
async def claim(ctx, id):
	await ctx.defer()
	
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	#check_update(game)
	await fix_shit(game, ctx.author)
	user_log(game, user, "claim", f"Target ID: {id}")
	done = 0
	faction = False
	for i in ctx.author.roles:
		#log.info(f"User Role Object: {i}, Name: {i.name}, Get Faction Result: {game.get_faction(name=i.name)}")
		if game.get_faction(name=i.name) != None:
			faction = i
			break
	if len(user.claims) >= game.action_limit and ctx.author.id not in exempt:
		await ctx.send(embed=error_embed("You have exceeded your maximum daily claims"))
		return

	result = game.claim(id, game.get_faction(name=faction.name))
	if result == "Sucessfully claimed":
		#await ctx.send(result)
		game.users[ctx.author.id].claims.append(id)
		log.info(f"User Claims: {game.users[ctx.author.id].claims}")
		game.save()
		temp = game.map()
		map_json = r_test.map_json(game.map_name)
		coordinates=map_json[f"l{id}"]["coordinates"]
		print(coordinates)
		image.snapshot(temp, eval(coordinates[0]))
		await ctx.send(embed=success_embed(f"Successfully claimed province {id}"),
		               file=discord.File("snapshot.png"))
	else:
		if result:
			await ctx.send(embed=error_embed(result))
		else: 
			await ctx.send(embed=error_embed("An error occurred, make sure you have a valid ID"))

	


@claim.error
async def claim_error(ctx: commands.Context, error):
	print(error)
	await ctx.send(embed=error_embed("You must be in a faction to use this command"))


#@client.command()
async def update_roles(ctx):
	game = r_test.load_from_id(ctx.guild.id)
	edited = []
	role_names = [i.name for i in ctx.guild.roles]
	for i in list(game.factions.values()):
		for j in i.roles:
			if game.server_id == ctx.guild.id:
				if j.central_id == 0 and j.central_name not in role_names:
					edited.append(j.central_name)
					role = await ctx.guild.create_role(
					    name=j.central_name,
					    color=discord.Color.from_rgb(i.colors[0], i.colors[1],
					                                 i.colors[2]),
					    hoist=True)
					j.central_id = role.id
				elif j.central_id != 0:
					role = ctx.guild.get_role(j.central_id)
					if not role:
						continue
					j.central_name = role.name
					await role.edit(color=discord.Color.from_rgb(
					    i.colors[0], i.colors[1], i.colors[2]))
					if not role.hoist:
						role.hoist = True
			elif i.server_id == ctx.guild.id:
				if j.satellite_id == 0 and j.satellite_name not in role_names:
					edited.append(j.central_name)
					role = await ctx.guild.create_role(
					    name=j.central_name,
					    color=discord.Color.from_rgb(i.colors[0], i.colors[1],
					                                 i.colors[2]),
					    hoist=True)
					j.central_id = role.id
				elif j.central_id != 0:
					role = ctx.guild.get_role(j.central_id)
					if not role:
						continue
					j.central_name = role.name
					print(j.central_name)
					if not role.hoist:
						role.hoist = True
					await role.edit(color=discord.Color.from_rgb(
					    i.colors[0], i.colors[1], i.colors[2]))
	game.save()
	#await ctx.send(f"Roles updated: {', '.join(edited)}")


@not_in_fac()
#@has_permissions(manage_channels=True, manage_roles=True)
@slash.slash(name="newfac",
             description="Create a new faction with the provided name",
             guild_ids=servers)
async def newfac(ctx, name):
	#Add config option later for restricting certain characters like :
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	await ctx.defer()
	user_log(game, user, "newfac", f"New Faction Name: {name}")
	if len(name) > 20 or len(name) < 1:
		await ctx.send(
		    "Faction name must be less than or equal to 20 characters and greater than zero"
		)
		return
	forbidden_characters = ["%", "Admin", "/", "\'", "\"", "."]
	for i in forbidden_characters:
		if i.lower() in name.lower():
			await ctx.send(embed=error_embed(f"You cannot have the character **{i}** in your faction name",title="Invalid Character"))
			return
	role_names = []
	for i in ctx.guild.roles:
		role_names.append(i.name)

	if name in role_names:
		await ctx.send(embed=error_embed("Role name already exists, try a different name"))
		return
	if game.create_faction(name) == "Faction name already exists":
		await ctx.send(embed=error_embed("Faction name already exists"))
		return
	print("begin updating roles")
	await update_roles(ctx)
	print("finished updating roles")
	game = r_test.load_from_id(ctx.guild.id)
	base_role = ctx.guild.get_role(game.factions[list(game.factions.keys())[-1]].roles[-2].central_id)
	user.faction = list(game.factions.keys())[-1]
	user.rank = game.factions[list(game.factions.keys())[-1]].roles[0].central_id
	game.users[user.id] = user
	leader_role = ctx.guild.get_role(game.factions[list(game.factions.keys())[-1]].roles[0].central_id)
	await ctx.author.add_roles(base_role, reason="Faction creation")
	await ctx.author.add_roles(leader_role, reason="Faction creation")
	await ctx.send(embed=success_embed(f"Created faction: **{name}**"))
	game.save()


@newfac.error
async def new_fac_error(ctx, error):
	log.error(f"Decorator Error: {error}")
	log.error(type(error))
	print(f"Error: {error}  end")
	print(type(error))
	if isinstance(error, commands.UnexpectedQuoteError) or isinstance(
	    error, commands.InvalidEndOfQuotedStringError):
		await ctx.send(embed=error_embed("Don't mess with quotes in the name" , title="Invalid Name"))
	elif isinstance(error, CheckFailure):
		await ctx.send(embed=error_embed("You must be factionless to use this command"))
	else:
		await ctx.send(embed=error_embed("An error occured, try a different name or contact Connor"))


@slash.slash(name="factions",
             description="List the current factions of this game",
             guild_ids=servers)
async def factions(ctx):
	game = r_test.load_from_id(ctx.guild.id)
	await ctx.send(str(game.faction_names()))

@dev()
@slash.slash(name="clearfacs",
             description="Clears all factions in game",
             guild_ids=servers)
async def clearfacs(ctx):
	await ctx.defer()
	game = r_test.load_from_id(ctx.guild.id)
	game.current_claims = {}
	for i in list(game.factions.values()):
		for j in i.roles:
			if j.central_id != 0:
				try:
					await ctx.guild.get_role(j.central_id).delete()
				except:
					print("Role deletion error")
	game.factions = {}
	game.save()
	print(game.current_claims)
	await ctx.send(embed=success_embed("Factions sucessfully cleared"))


@clearfacs.error
async def clearfacs_error(ctx, error):
	await ctx.send("You must be a dev to use this command")

@dev()
@slash.slash(name="delete_fac",
             description="Deletes selected faction",
             guild_ids=servers)
async def delete_fac(ctx, faction):
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	user_log(game, user, "delete_fac", f"Target Faction: {faction}")
	faction_obj = game.get_faction(name=faction)
	if not faction_obj:
		await ctx.send(embed=error_embed("Target faction must exist. Make sure you spelled it right"))
		log.warning(f"Target Faction Result: {faction_obj} - Target Faction Name: {faction} - Game Factions: {game.factions}")
		return
	log.info(f"DELETE FAC USER FACTION INFO")
	for i in list(game.users.values()):
		log.info(f"User Name: {i.name} - User Faction: {i.faction}")
		if isinstance(i.faction,class_playground.Faction):
			if i.faction.id == faction_obj.id:
				i.faction = ""
	for i in faction_obj.roles:
			if i.central_id != 0:
				try:
					await ctx.guild.get_role(i.central_id).delete()
				except:
					log.error(f"Role deletion error for role: {ctx.guild.get_role(i.central_id)}")
	for i in list(game.current_claims.keys()):
		if game.current_claims[i] == faction_obj.id:
			game.current_claims.pop(i)
	for i in list(game.game_json.keys()):
		if game.game_json[i] == faction_obj.id:
			game.game_json.pop(i)
	game.factions.pop(faction_obj.id)
	game.save()
	await ctx.send(f"Faction **{faction}** successfully deleted")
	



@slash.slash(name="myfac",
             description="Gives the name of the faction you are in",
             guild_ids=servers)
async def myfac(ctx):
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	user_log(game, user, "myfac", "N/A")
	#check_update(game)
	for i in ctx.author.roles:
		if game.get_faction(name=i.name) != None:
			await ctx.send(i.name)
			return
	await ctx.send(embed=error_embed("You are not in a faction. Use /join to join one"))


@slash.slash(name="dorito", description="dorito", guild_ids=servers)
async def dorito(ctx):
	print(ctx.author)
	print(ctx.author.id)
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	user_log(game, user, "dorito", "DORITO")
	embed = discord.Embed(color=0xe69701)
	embed.title = "the dorito"
	embed.set_image(
	    url=
	    "https://media.discordapp.net/attachments/774773624396972042/776205016423464980/dorito.gif"
	)
	await ctx.send(embed=embed)

@slash.slash(name="log", description="Uploads the log for debugging", guild_ids=servers)
async def log_command(ctx):
	
	with open('logfile.log', 'r') as fin:
		data = fin.read().splitlines(True)
	with open('shortlog.log', 'w') as fout:
		fout.writelines(data[7:])
	file = discord.File("shortlog.log")
	await ctx.send("Here's the log", file=file)



@dev()
@slash.slash(name="update", description="*/1 * * * *", guild_ids=servers)
async def update(ctx, schedule):
	game = r_test.load_from_id(ctx.guild.id)
	param = "test"

	async def filler():
		return await map_update(param)

	game.schedule = schedule
	#check_update(game)
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
@slash.slash(name="delete_game",
             description="Permanently deletes the current game",
             guild_ids=servers)
async def delete_game(ctx):
	game = r_test.load_from_id(ctx.guild.id)
	for i in list(game.factions.values()):
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


@slash.slash(name="size",
             description="Returns size of the game object in bytes",
             guild_ids=servers)
async def size(ctx):
	game = r_test.load_from_id(ctx.guild.id)
	await ctx.send(f"The game size is {round(game.game_size()/1000000, 2)} MB")


@slash.slash(name="new_claims",
             description="Shows the map of the claims made this udpate",
             guild_ids=servers)
async def new_claims(ctx):
	await ctx.defer()
	game = r_test.load_from_id(ctx.guild.id)
	image = game.current_claims_map()
	if image != "No map":
		image.save("current.png")
		await ctx.send(file=discord.File("current.png"))

	else:
		await ctx.send(
		    "No map found for current game. Try using /add_map first")


@in_fac()
@leader()
@slash.slash(name="change_faction_color",
             description="Changes the faction color to the given RGB values",
             guild_ids=servers)
async def change_faction_color(ctx, color):
	await ctx.defer()
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	user_log(game, user, "change_faction_color", f"New Color: {color}")
	faction = user.faction
	leader = False


	await ctx.send("Faction colors don't update until after a map update or redraw.")
	colors = color.strip().split(",")
	if len(colors) != 3:
		embed = discord.Embed(title="Change Faction Color!", description="You need exactly three values (RGB) to change the color.\nTry something like **0, 0, 255**",color=0x96d031)
		embed.set_image(url="https://media1.tenor.com/images/b3b66ace65470cba241193b62366dfee/tenor.gif")
		await ctx.send(embed=embed)
		return
	for index, i in enumerate(colors):
		print(int(i))
		if not i.strip().isdigit():
			await ctx.send(embed=error_embed("The RGB values must be numbers"))
			return
		if int(i) > 254 or int(i) < 0:
			await ctx.send(embed=error_embed("The RGB values must be between 0 and 254"))
			return
		colors[index] = int(i.strip())
	if colors == [0,0,0] or colors == [255,255,255] or colors ==[97,175,253]:
		await ctx.send(embed=error_embed("You cannot change your faction color to black or white"))
		return	
	print(colors)
	for i in faction.roles:
		i.colors = colors
	faction.colors = colors

	game.factions[faction.id] = faction
	game.save()
	await update_roles(ctx)

	await ctx.send(embed=success_embed("Faction color updated"))


@change_faction_color.error
async def change_faction_color_error(ctx: commands.Context, error):
	print(error)
	if isinstance(error, CheckFailure):
		await ctx.send(embed=error_embed("You must be in a faction to use this command"))


@dev()
@slash.slash(name="manual_update",
             description="Manually update the map",
             guild_ids=servers)
async def manual_update(ctx):
	await ctx.send("Sending update...")
	await map_update(ctx.guild.id)

@manual_update.error
async def manual_update_error(ctx, error):
	print(error)
	if isinstance(error, CheckFailure):
		await ctx.send(embed=error_embed("You must be a dev to use this command"))
	else:
		await ctx.send(embed=error_embed("An error has occurred"))


@slash.slash(name="id_map",
             description="Shows the id map for the current map",
             guild_ids=servers)
async def id_map(ctx):
	await ctx.defer()
	await ctx.send(
	    "https://media.discordapp.net/attachments/878093499399041095/884572546673029151/Extremist_Map_3_Province_Map_Water_Connection_.png"
	)

@dev()
@slash.slash(name="redraw_map",
             description="Manually update the map",
             guild_ids=servers)
async def redraw_map(ctx):
	game = r_test.load_from_id(ctx.guild.id)
	log.info(game.game_json)
	await ctx.send("Redrawing")
	game.redraw_map()
	game.save()


@manual_update.error
async def manual_update_error(ctx, error):
	print(error)
	if isinstance(error, CheckFailure):
		await ctx.send(embed=error_embed("You must be a dev to use this command"))
	else:
		await ctx.send(embed=error_embed("An error has occurred"))

@slash.slash(name="get_connected", description="Get the ids of all provinces connected to the province with the given id", guild_ids=servers)
async def get_connected(ctx, id):
	game = r_test.load_from_id(ctx.guild.id)
	map_data = r_test.map_json(game.map_name)
	if map_data != "Invalid JSON":
		data = map_data.get("l"+id)
		if data != None:
			result = []
			for i in data["neighbors"]:
				if "l" in i:
					result.append(i[1:])
				else:
					result.append(f"{i[1:]} (water)")
			await ctx.send(f'Connected IDs for Province {id}:\n{", ".join(result)}')

@slash.slash(name="unclaim", description="Unclaims a province with the given ID that you have claimed this update", guild_ids=servers)
async def unclaim(ctx, id):
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	user_log(game, user, "unclaim", f"Target Province: {id}")
	await ctx.defer()
	if id in user.claims:
		user.claims.remove(id)
		game.current_claims.pop(id)
		temp = Image.open("test.png").convert('RGB')
		map_json = r_test.map_json(game.map_name)
		coordinates=map_json[f"l{id}"]["coordinates"]
		for i in coordinates:
			image.quick_fill(temp, eval(i), (255,255,255), pattern=0, pattern_color=(1, 1, 1, 1), inverted_pattern=False)
		temp.save("test.png")
		game.update_map(temp)
		game.save()
		await ctx.send(embed=success_embed(f"Successfully unclaimed Province {id}"),file=discord.File("test.png"))
	else:
		await ctx.send(embed=error_embed(f"**{id}** is an invalid ID. Make sure that the ID exists and you claimed it this update", title="Invalid ID"))

@upper_midrank()
@slash.subcommand(base="trade", name="propose", description="Propose a new trade", guild_ids=servers)
async def trade_propose(ctx, faction, offer, request):
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	user_log(game, user, "trade propose", f"Target Faction: {faction} - Offer: {offer} - Request: {request}")
	user_fac_obj = user.faction
	fac_obj = game.get_faction(name=faction)
	if fac_obj == None:
		await ctx.send(embed=error_embed("Invalid target faction"))
		return
	if user_fac_obj == fac_obj:
		await ctx.send(embed=error_embed("You cannot send a trade to your own faction"))
		return
	print(offer.split(","))
	offer_list = []
	request_list = []
	for i in offer.split(","):
		id = i.strip()
		if id.lower() == "none":
			offer_list = ["none"]
			break
		if id.isdigit():
			if game.game_json.get(id) != None:
				if id in offer_list:
					await ctx.send(embed=error_embed(f"You can't offer Province ID: {id} twice. Make sure you have no duplicates in your offer(s) and request(s)"))
					return
				offer_list.append(id)
			else:
				await ctx.send(embed=error_embed(f"Province ID: {id} does not exist"))
				return
		else:
			await ctx.send(embed=error_embed(f"Invalid offer input: {i}"))
			return

	for i in request.split(","):
		id = i.strip()
		if id.lower() == "none":
			if offer_list == ["none"]:
				await ctx.send(embed=error_embed("Something must be traded, cannot request empty trades"))
				return
			request_list = ["none"]
			break
		if id.isdigit():
			if game.game_json.get(id) != None:
				if id in offer_list:
					await ctx.send(embed=error_embed(f"You can't offer and request Province ID: {id}. Make sure you have no duplicates in your offer(s) and request(s)"))
					return
				if id in request_list:
					await ctx.send(embed=error_embed(f"You can't request Province ID: {id} twice. Make sure you have no duplicates in your offer(s) and request(s)"))
					return					
				request_list.append(id)
			else:
				await ctx.send(embed=error_embed(f"Province ID: {id} does not exist"))
				return			
		else:
			await ctx.send(embed=error_embed(f"Invalid request input: {i}"))
			return
	
	for i in list(game.trades.keys()):
		if game.trades[i]["Offering"] == offer_list and game.trades[i]["Requesting"] == request_list:
			await ctx.send(embed=error_embed(f"Cannot create a duplicate trade. "))

	trade_id = str(random.randint(1111,9999))
	while game.trades.get(trade_id) != None:
		trade_id = str(random.randint(1111,9999))
	offer_list.sort()
	request_list.sort()
	game.trades[trade_id] = {"From":user_fac_obj.id, "To":fac_obj.id, "Offering":offer_list, "Requesting":request_list}

	await ctx.send(embed=success_embed("Trade listed"))
	await ctx.send(str(game.trades))
	game.save()

def trade_check(trade, user, faction, game):
	if trade == None:
		return "Trade ID does not exist"
		
		
	if trade["To"] != faction.id:
		return "You must be in the target faction to accept this trade"
	attack_list = list(game.attacks.keys())
	for i in trade["Offering"]:
		if str(i) in attack_list:
			return "You cannot trade a province that is being attacked"
	for i in trade["Requesting"]:
		if str(i) in attack_list:
			return "You cannot trade a province that is being attacked"
	errors_offer=[]
	errors_request=[]
	for i in trade["Offering"]:
		if game.game_json[i] != trade["From"]:
			errors_offer.append(i)

	for i in trade["Requesting"]:
		if game.game_json[i] != trade["To"]:
			errors_request.append(i)

	if len(errors_offer) + len(errors_request) > 0:
		message = ""
		if len(errors_offer) > 0:
			message += f"\nOffering faction does not own province ID(s): {', '.join(errors_offer)}"
		if len(errors_request) > 0:
			message += f"\nYour faction does not own province ID(s): {', '.join(errors_request)}"
		return f"Cannot accept trade, see the following errors:{message}"

@slash.subcommand(base="trade", name="preview", description="Look at a trade", guild_ids=servers)
async def trade_preview(ctx, trade_id):
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	
	if isinstance(user.faction, class_playground.Faction):
		faction = user.faction
	elif user.faction != "":
		faction = game.get_faction(name=user.faction)
	else:
		await ctx.send(embed=error_embed("Cannot find faction"))
		return
	trade = game.trades.get(trade_id)
	user_log(game, user, "trade preview", f"Trade ID: {trade_id} - Trade Info: {trade}")
	await ctx.defer()
	result = trade_check(trade, user, faction, game)
	if result != None and result != "You must be in the target faction to accept this trade":
		await ctx.send(result)
		return

	temp = Image.open(io.BytesIO(base64.b64decode(r_test.map_image(game.map_name)))).convert('RGB')
	
	color = tuple(game.get_faction(id=trade["From"]).colors)
	map_json = r_test.map_json(game.map_name)
	for i in trade["Offering"]:
		print(i)
		coordinates=map_json[f"l{i}"]["coordinates"]
		for j in coordinates:
			image.quick_fill(temp, eval(j), color)
	
	color = tuple(game.get_faction(id=trade["To"]).colors)
	for i in trade["Requesting"]:
		coordinates=map_json[f"l{i}"]["coordinates"]
		for j in coordinates:
			image.quick_fill(temp, eval(j), color)
	
	temp.save("trade.png")
	await ctx.send(file=discord.File("trade.png"))
	game.save()

@upper_midrank()
@slash.subcommand(base="trade", name="accept", description="Accept a trade", guild_ids=servers)
async def trade_accept(ctx, trade_id):
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	if isinstance(user.faction, class_playground.Faction):
		faction = user.faction
	elif user.faction != "":
		faction = game.get_faction(name=user.faction)
	else:
		await ctx.send(embed=error_embed("Cannot find faction"))
		return

	trade = game.trades.get(trade_id)
	user_log(game, user, "trade accept", f"Trade ID: {trade_id} - Trade Info: {trade}")
	await ctx.defer()
	result = trade_check(trade, user, faction, game)
	if result != None:
		await ctx.send(result)
		return
	print("offering")
	for i in trade["Offering"]:
		print(i)
		print(trade["To"])
		game.game_json[i] = trade["To"]
	print("requesting")
	for i in trade["Requesting"]:
		print(i)
		print(trade["To"])
		game.game_json[i] = trade["From"]
	game.trades.pop(trade_id)
	temp=game.redraw_map()
	temp.save("map.png")
	await ctx.send(file=discord.File("map.png"))
	game.save()

@slash.subcommand(base="trade", name="view", description="View trades", guild_ids=servers)
async def trade_view(ctx):
	game = r_test.load_from_id(ctx.guild.id)	
	user = game.get_user(ctx.author.id)
	user_log(game, user, "trade view", f"Trade List: {game.trades}")
	if isinstance(user.faction, class_playground.Faction):
		faction = user.faction
	elif user.faction != "":
		faction = game.get_faction(name=user.faction)
	else:
		await ctx.send(embed=error_embed("Cannot find faction"))
		return
	embed = discord.Embed(color=0x1111ee)
	for i in list(game.trades.keys()):
		trade = game.trades[i]
		if trade["From"] == faction.id or trade["To"] == faction.id:
			embed.add_field(name=f"Trade ID: {i}", value=f"From: {game.get_faction(id=trade['From']).name}\nTo: {game.get_faction(id=trade['To']).name}\nOffering: {', '.join(trade['Offering'])}\nRequesting: {', '.join(trade['Requesting'])}")
	await ctx.send(embed=embed)
	
async def complete_attack(ctx, id):
	game = r_test.load_from_id(ctx.guild.id)
	print(game.attacks)
	print(game.attacks.get(id))
	attack_info = game.attacks.get(id)
	log.info(f'ATTACK INFO: {attack_info}')
	if len(attack_info["attackers"]) != attack_info["max_attackers"] or len(attack_info["defenders"]) != attack_info["max_defenders"]:
		return
	attack_dice = []
	defense_dice = []
	for i in range(attack_info["max_attackers"]):
		attack_dice.append(random.randint(1,6))
	for i in range(attack_info["max_defenders"]):
		defense_dice.append(random.randint(1,6))
	attack_dice.sort(reverse=True)
	defense_dice.sort(reverse=True)

	embed = discord.Embed(title="**BATTLE RESULTS**", color = 0x5ac30a)
	embed.add_field(name="***Defender Victory!***",value=f"The attackers were repealed in a glorious defense of province {id}!")
	embed.set_thumbnail(url="https://cdn2.iconfinder.com/data/icons/rpg-fantasy-game-skill-ui/512/game_skill_ui_guard_shield_broken_sword-512.png")
	if sum(defense_dice) < sum(attack_dice):
		game.game_json[id] = game.game_json[attack_info["attacking_province"]]
		win = True
		embed = discord.Embed(title="**BATTLE RESULTS**", color = 0xf92424)
		embed.set_thumbnail(url="https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fclipart-library.com%2Fimg1%2F1063584.png&f=1&nofb=1")
		embed.add_field(name="***Attacker Victory!***", value=f"A righteous victory over the enemy was achieved at province {id}!")
	game.save()
	embed.add_field(name="Attack Dice", value=f"Attack Dice Rolls: `{', '.join(str(i) for i in attack_dice)}`\nSum Total: {sum(attack_dice)}", inline=False)
	embed.add_field(name="Defense Dice", value=f"Defense Dice Rolls: `{', '.join(str(i) for i in defense_dice)}`\nSum Total: {sum(defense_dice)}", inline=False)
	base_coords = r_test.map_json(game.map_name)[f"l{id}"]["coordinates"][0]
	base_coords = eval(base_coords)
	img = game.map()
	image.snapshot(img, base_coords)
	embed.set_image(url="attachment://snapshot.png")
	game.attacks.pop(id)
	temp=game.redraw_map()
	temp.save("map.png")
	await ctx.send(embed=embed,file=discord.File("snapshot.png"))
	game.save()

@slash.subcommand(base="engage",name="commence", description="Attack the target province", guild_ids=servers)
async def attack(ctx, attacker, target):
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	user_log(game, user, "engage commence", f"Attacking Province: {attacker} - Target Province: {target}")
	await fix_shit(game, ctx.author)
	faction = user.faction
	target_owner = game.game_json.get(target)
	log.info(f"\nCOMMAND INFO:\nCommand: engage commence - Target Faction Province: {target}")
	log.info(f"Target Owner: {target_owner}")
	log.info(f"Current Claims: {game.current_claims}")
	#for i in game.factions:
	#	log.info(f"Iteration: {i}")
	#	log.info(f"Faction: {game.factions[i]}")
	#	log.info(f"Faction Name: {game.factions[i].name}")
	if user.actions >= game.action_limit:
		await ctx.send(embed=error_embed("You have used up all of your actions for this update period"))
		return
	if target_owner == None:
		await ctx.send(embed=error_embed("Invalid target ID"))
		return
	if target_owner == 0:
		await ctx.send(embed=error_embed("You cannot attack an empty province"))
		return
	if target_owner == faction.id:
		await ctx.send(embed=error_embed("You cannot attack your own province"))
		return
	if game.game_json.get(attacker) != faction.id:
		print(f"attacker {faction.id}")
		print(f"Real Owner {game.game_json.get(attacker)}")
		await ctx.send("You must own the attacking province for at least one round")
		return
	if game.attacks.get(target) != None:
		await ctx.send(embed=error_embed("This province is already being attacked"))
		return
	target_full = r_test.map_json(game.map_name)[f"l{target}"]
	print(target_full)
	neighbor_ids = [i[1:] for i in target_full["neighbors"] if "l" in i]
	defense_count = 1
	for i in neighbor_ids:
		if game.game_json.get(i) == target_owner:
			defense_count += 1

	attacker_full = r_test.map_json(game.map_name)[f"l{attacker}"]
	neighbor_ids = [i[1:] for i in attacker_full["neighbors"] if "l" in i]
	attack_count = 0
	
	for i in neighbor_ids:
		if game.game_json.get(i) == faction.id:
			attack_count += 1
	
	if attack_count == 0:
		await ctx.send(embed=error_embed("You must own at least one neighboring province in order to attack"))
		return

	game.attacks[f"{target}"] = {"attacking_province": attacker, "defending_province": target,"attackers":[user.discord_id], "defenders":[0], "max_attackers":attack_count, "max_defenders":defense_count, "instigator": user.discord_id}
	user.actions += 1
	await ctx.send(f"**Attacking province {target} from province {attacker}**\nMaximum Attackers: {attack_count}\nMaximum Defenders: {defense_count}")
	game.save()
	await complete_attack(ctx, target)


@slash.subcommand(base="engage",name="join", description="Become an attacaker or defender of the given province", guild_ids=servers)
async def engage(ctx, id):
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	await fix_shit(game, ctx.author)
	faction = user.faction
	attacker_or_defender = None
	attack_info = game.attacks.get(id)
	if attack_info == None:
		await ctx.send(embed=error_embed("Invalid Province ID, make sure that ID exists and is being attacked"))
		return
	
	if faction.id == game.game_json.get(id):
		attacker_or_defender = "defender"
		if user.discord_id in attack_info["defenders"]:
			await ctx.send(embed=error_embed("You are already defending"))
			return
		if len(attack_info["defenders"]) >= attack_info["max_defenders"]:
			await ctx.send(embed=error_embed("You cannot engage in this defense, there is already the maximum number of defenders engaged"))
			return
	elif faction.id == game.game_json.get(attack_info["attacking_province"]):
		attacker_or_defender = "attacker"
		if user.discord_id in attack_info["attackers"]:
			await ctx.send(embed=error_embed("You are already attacking"))
			return
		if len(attack_info["attackers"]) >= attack_info["max_attackers"]:
			await ctx.send(embed=error_embed("You cannot engage in this attack, there is already the maximum number of attackers engaged"))
			return
	if attacker_or_defender is None:
		await ctx.send(embed=error_embed("You must be in either the attacking or defending faction to engage"))
		return
	user_log(game, user, "engage join", f"Target Province: {id} - Attacker or Defender: {attacker_or_defender}")
	if user.actions >= game.action_limit:
		await ctx.send(embed=error_embed("You have used up all of your actions for this update period"))
		return
	game.attacks[id][f"{attacker_or_defender}s"].append(user.discord_id)
	user.actions += 1
	await ctx.send(f'Successfully became {attacker_or_defender} for province {id}.\nNew Totals:\nAttackers Committted: {len(game.attacks[id]["attackers"])}, Max Attackers: {attack_info["max_attackers"]}\nCurrent Defenders: {len(game.attacks[id]["defenders"])}, Max Defenders: {attack_info["max_attackers"]}')
	game.save()
	await complete_attack(ctx, id)

@slash.subcommand(base="engage", name="info", description="See the info of a battle", guild_ids=servers)
async def engage_info(ctx, id):
	game = r_test.load_from_id(ctx.guild.id)
	attack_info = game.attacks.get(id)
	if attack_info == None:
		await ctx.send(embed=error_embed("Invalid Province ID, make sure that ID exists and is being attacked"))
		return
	embed = discord.Embed(title="**BATTLE INFORMATION**",color=0xd8320b)
	embed.add_field(name="Defenders Committed", value=f'{len(game.attacks[id]["defenders"])} of {attack_info["max_defenders"]} allowed', inline=False)
	embed.add_field(name="Attackers Committed", value=f'{len(game.attacks[id]["attackers"])} of {attack_info["max_attackers"]} allowed', inline=False)
	embed.set_footer(text="Defenders have a base defense of 1 and may exceed what their province limit would otherwise allow by one.")
	base_coords = r_test.map_json(game.map_name)[f"l{id}"]["coordinates"][0]
	print(eval(base_coords))
	base_coords = eval(base_coords)
	img = game.map()
	image.snapshot(img, base_coords)
	embed.set_image(url="attachment://snapshot.png")
	await ctx.send(embed=embed, file=discord.File("snapshot.png"))
	
@dev()
@slash.slash(name="delete_attack", description=":troll:", guild_ids=servers)
async def delete_attack(ctx, id):
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	if game.attacks.get(id)!=None:
		game.attacks.pop(id)
	await ctx.send(f"Deleted Attack ID: {id}")
	user_log(game, user, "delete_attack", f"Attack ID: {id}")
	game.save()

@dev()
@slash.slash(name="edit_max_actions", description="Self explanitory", guild_ids=servers)
async def edit_max_actions(ctx, max):
	game=r_test.load_from_id(ctx.guild.id)
	game.action_limit = int(max)
	await ctx.send(f"New max: {max}")
	game.save()

@in_fac()
@midrank()
@slash.slash(name="promote", description="Promotes the pinged user", guild_ids=servers)
async def promote(ctx, target_user):
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	user_log(game, user, "promote", f"Target User: {target_user[3:-1]}")
	if "!" in target_user:
		sliced_user = target_user[3:-1]
	else:
		sliced_user = target_user[2:-1]
	try:
		target = game.users.get(int(sliced_user))
	except:
		await ctx.send(embed=error_embed(f"{target_user} is not a valid target user. Make sure you typed everything correctly and try again or contact Connor",title="Invalid Target User"))
	print(target)
	if not target:
		await ctx.send(embed=error_embed(f"{target_user} is not a valid target user. Make sure you typed everything correctly and try again or contact Connor",title="Invalid Target User"))
	print(target.faction)
	print(user.faction)
	if target.faction != user.faction:
		await ctx.send(embed=error_embed("Target user must be in your faction"))
	role_dict={}
	user_perms = 10
	target_perms = 10
	for i in user.faction.roles:
		role_dict[i.central_id] = i.perm_id
		role_dict[i.satellite_id] = i.perm_id
	print("Testing 2")
	for i in ctx.guild.get_member(int(sliced_user)).roles:
		id_result = role_dict.get(i.id)
		if id_result:
			if id_result < target_perms:
				target_perms = id_result
	for i in ctx.author.roles:
		id_result = role_dict.get(i.id)
		if id_result:
			if id_result < user_perms:
				user_perms = id_result
	print(user_perms)
	print(target_perms)
	if target_perms == 2:
		await ctx.send(embed=error_embed("You cannot swap leadership yet"))
		return
	if user_perms >= target_perms:
		await ctx.send(embed=error_embed("You cannot promote someone at or above your rank"))
		return
	role = ctx.guild.get_role(user.faction.roles[target_perms-2].central_id)
	await ctx.guild.get_member(int(sliced_user)).add_roles(role)
	role2 = ctx.guild.get_role(user.faction.roles[target_perms-1].central_id)
	await ctx.guild.get_member(int(sliced_user)).remove_roles(role2)
	await ctx.send(embed=success_embed(f"{target_user} has now been promoted to {role.name}"))

@in_fac()
@midrank()
@slash.slash(name="demote", description="Promotes the pinged user", guild_ids=servers)
async def demote(ctx, target_user):
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	user_log(game, user, "demote", f"Target User: {target_user[2:-1]}")
	if "!" in target_user:
		sliced_user = target_user[3:-1]
	else:
		sliced_user = target_user[2:-1]

	try:
		target = game.users.get(int(sliced_user))
	except:
		await ctx.send(embed=error_embed(f"{target_user} is not a valid target user. Make sure you typed everything correctly and try again or contact Connor",title="Invalid Target User"))
	print(target)
	if not target:
		await ctx.send(embed=error_embed(f"{target_user} is not a valid target user. Make sure you typed everything correctly and try again or contact Connor",title="Invalid Target User"))
	print(target.faction)
	print(user.faction)
	if target.faction != user.faction:
		await ctx.send(embed=error_embed("Target user must be in your faction",title="Invalid Target User"))
	role_dict={}
	user_perms = 10
	target_perms = 10
	for i in user.faction.roles:
		role_dict[i.central_id] = i.perm_id
		role_dict[i.satellite_id] = i.perm_id
	print("Testing 2")
	for i in ctx.guild.get_member(int(sliced_user)).roles:
		id_result = role_dict.get(i.id)
		if id_result:
			if id_result < target_perms:
				target_perms = id_result
	for i in ctx.author.roles:
		id_result = role_dict.get(i.id)
		if id_result:
			if id_result < user_perms:
				user_perms = id_result
	print(user_perms)
	print(target_perms)
	if target_perms > 5:
		await ctx.send(embed=error_embed("You cannot demote a simple member yet"))
		return
	if user_perms >= target_perms:
		await ctx.send(embed=error_embed("You cannot demote someone at or above your rank"))
		return
	role = ctx.guild.get_role(user.faction.roles[target_perms].central_id)
	await ctx.guild.get_member(int(sliced_user)).add_roles(role)
	role2 = ctx.guild.get_role(user.faction.roles[target_perms-1].central_id)
	await ctx.guild.get_member(int(sliced_user)).remove_roles(role2)
	await ctx.send(embed=success_embed(f"{target_user} has now been demoted to {role.name}"))

@in_fac()
@midrank()
@slash.slash(name="accept", description="Accepts the pinged user", guild_ids=servers)
async def accept(ctx, target_user):
	game = r_test.load_from_id(ctx.guild.id)
	user = game.get_user(ctx.author.id)
	user_log(game, user, "accept", f"Target User: {target_user[2:-1]}")
	print(target_user[3:-1])
	if "!" in target_user:
		sliced_user = target_user[3:-1]
	else:
		sliced_user = target_user[2:-1]
	try:
		target = game.users.get(int(sliced_user))
		log.info(f"Target user result: {target} - target user id: {int(sliced_user)}")
		log.info(f"Game Users: {game.users}")
	except:
		await ctx.send(embed=error_embed(f"{target_user} is not a valid target user. Make sure you typed everything correctly and try again or contact Connor",title="Invalid Target User"))
		return
	print(target)
	if not target:
		await ctx.send(embed=error_embed(f"{target_user} is not a valid target user. Make sure you typed everything correctly and try again or contact Connor",title="Invalid Target User"))
		return
	print(target.faction)
	print(user.faction)
	role = ctx.guild.get_role(user.faction.roles[-2].central_id)
	target_discord_user = ctx.guild.get_member(int(sliced_user))
	if role in target_discord_user.roles:
		await ctx.send(embed=error_embed("You cannot accept someone already in your faction"))
		return
	target.rank = user.faction.roles[-2].central_id
	game.users[sliced_user] = target
	await ctx.guild.get_member(int(sliced_user)).add_roles(role)
	role = ctx.guild.get_role(user.faction.roles[-3].central_id)
	await ctx.guild.get_member(int(sliced_user)).add_roles(role)
	role = ctx.guild.get_role(user.faction.roles[-1].central_id)
	await ctx.guild.get_member(int(sliced_user)).remove_roles(role)
	await ctx.send(embed=success_embed(f"{target_user} has been accepted into {user.faction.name}"))
	game.save()
@accept.error
async def accept_error(ctx, error):
	log.error(f"Accept Error: {error}")
	log.error(type(error))
	print(type(error))
	if isinstance(error, CheckFailure):
		await ctx.send(embed=error_embed("You must be a midrank or higher to accept applicants",title="Invalid Ranking"))
	else:
		await ctx.send(embed=error_embed("An error occured, try a different name"))
client.run(os.environ['api'])
asyncio.get_event_loop().run_forever()
