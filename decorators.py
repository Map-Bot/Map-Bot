from discord.ext import commands
import r_test
from discord_slash.utils.manage_commands import create_choice, create_option

devs = [339251879273955330, 750744079079440506, 244638942169792513]

def dev():
    async def predicate(ctx):
        return ctx.author.id in devs
    return commands.check(predicate)

def get_faction(ctx):
    game = r_test.load_from_id(ctx.guild.id)
    for i in ctx.author.roles:
        value = game.get_faction(i.name)
        if value != None:
            return value

def in_fac():
    async def predicate(ctx):
        faction = get_faction(ctx)
        if faction == None:
            return False
        return True
    return commands.check(predicate)


def not_in_fac():
    async def predicate(ctx):
        faction = get_faction(ctx)
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