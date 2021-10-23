from discord.ext import commands
import r_test

def test_predicate():
    async def predicate(ctx):
        #await ctx.send("Test worked, cool")
        return True
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