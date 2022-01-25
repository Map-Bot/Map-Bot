from discord.ext import commands
import r_test
from discord_slash.utils.manage_commands import create_choice, create_option

devs = [339251879273955330, 750744079079440506, 244638942169792513,811024803292905532]

def dev():
    async def predicate(ctx):
        return ctx.author.id in devs
    return commands.check(predicate)

def get_faction(ctx, id):
    game = r_test.load_from_id(ctx.guild.id)
    for i in ctx.author.roles:
        value = game.get_faction(i.name)
        if value != None:
            print(f"GETTING USER HERE: {ctx.author.id}")
            user = game.get_user(ctx.author.id)
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
    return commands.check(predicate)


def not_in_fac():
    async def predicate(ctx):
        #it works, dont touch
        faction = get_faction(ctx,ctx.author.id)
        if faction != None:
            return False
        return True
    return commands.check(predicate)
    
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
    return commands.check(predicate)
  """