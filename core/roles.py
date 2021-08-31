import asyncio

async def repair_roles(ctx, roles):
  pass


async def purge_roles(ctx):
  for i in ctx.guild.roles:
    print(i)
    print(i.is_bot_managed())
    if "Faction" in i.name:
      await i.delete()