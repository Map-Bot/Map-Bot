from discord.ext import commands
from interactions.ext.checks import check
import r_test
#from discord_slash.utils.manage_commands import create_choice, create_option
import class_playground
devs = [339251879273955330, 750744079079440506, 244638942169792513, 811024803292905532]

def dev():
    async def predicate(ctx):
        return ctx.author.id in devs
    return check(predicate)

def get_faction(ctx, id):
    game = r_test.load_from_id(ctx.guild.id)
    print(ctx.author.roles)
    user = game.get_user(ctx.author.id)
    for i in ctx.author.roles:
        print("stupid")
        value = game.get_faction(i.name)
        if value != None:
            print("found")
            print(f"GETTING USER HERE: {ctx.author.id}")
            
            user.faction = value
            print(ctx.author)
            game.users[id] = user
            game.save()
            return value 
    game.users[id].faction = ""
    print("No Faction Found")
    game.save()

def in_fac():
    async def predicate(ctx):
        faction = get_faction(ctx,ctx.author.id)
        if faction == None:
            return False
        return True
    return check(predicate)


def not_in_fac():
    async def predicate(ctx):
        #it works, dont touch
        faction = get_faction(ctx,ctx.author.id)
        if faction != None:
            return False
        return True
    return check(predicate)

def get_perms(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    user = game.get_user(ctx.author.id)
    faction = get_faction(ctx,ctx.author.id)
    if not faction:
        return
    perms = 5
    role_dict = {}
    if not isinstance(faction, class_playground.Faction):
        print("NO FACTION")
        return
    print("Testing 1")
    for i in faction.roles:
        role_dict[i.central_id] = i.perm_id
        role_dict[i.satellite_id] = i.perm_id
    print("Testing 2")
    for i in ctx.author.roles:
        id_result = role_dict.get(i.id)
        if id_result:
            if id_result < perms:
                perms = id_result
    print("Testing 3")
    return perms
    
def leader():
    async def predicate(ctx):
        result = get_perms(ctx)
        if not result:
            return False
        if result < 2:
            return True
        else:
            return False
    return check(predicate)
def lieutenant():
    async def predicate(ctx):
        result = get_perms(ctx)
        if not result:
            return False
        if result < 3:
            return True
        else:
            return False
    return check(predicate)
def upper_midrank():
    async def predicate(ctx):
        result = get_perms(ctx)
        if not result:
            return False
        if result < 4:
            return True
        else:
            return False
    return check(predicate)
def midrank():
    async def predicate(ctx):
        result = get_perms(ctx)
        if not result:
            return False
        if result < 5:
            return True
        else:
            return False
    return check(predicate)
"""
def not_in_fac():
    async def predicate(ctx):
        game = r_test.load_from_id(ctx.guild.id)
        for i in ctx.author.roles:
            if game.get_faction(i.name) != None:
                await ctx.send("You must be factionless to use this command")
                raise Error1
                return False

        return True
    return check(predicate)
  """