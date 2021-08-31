import discord
from discord.ext import commands
import files

def not_in_faction():
  def predicate(ctx):
    roles = files.game_roles(ctx.guild.id)
    print(roles)
    author_roles = []
    for i in ctx.author.roles:

      if i.name in list(roles.keys()):
        print("in faction")
    return True
  return commands.check(predicate)