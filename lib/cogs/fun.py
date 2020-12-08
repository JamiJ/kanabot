from random import choice, randint
from typing import Optional

from discord import Member
from discord.ext.commands import Cog
from discord.ext.commands import BadArgument
from discord.ext.commands import command


class Fun(Cog):
	def __init__(self, bot):
		self.bot = bot

	#@command(name="test", aliases=["command", "c"], hidden=True)

	@command(name="hello", aliases=["hi"])
	async def say_hello(self, ctx):
		await ctx.send(f"{choice(('Hello', 'Hi', 'Hey'))} {ctx.author.mention}!")

#	@command(name="dice", aliases=["roll"])
#	async def roll_dice(self, ctx, die_string: str):
#		dice, value = (int(term) for term in die_string.split("d"))
#		rolls = [randint(1, value) for i in range(dice)]
#
#		await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum.(rolls)}")

	@command(name="slap", aliases=["hit"])
	async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = " for no reason"):
		await ctx.send(f"{ctx.author.display_name} slapped {member.mention} {reason}!")

	@slap_member.error
	async def slap_member_error(self, ctx, exc):
		if isinstance(exc, BadArgument):
			await ctx.send("Cannot find this member")

	@command(name="echo", aliases=["say"])
	async def echo_message(self, ctx, *, message):
		await ctx.message.delete()
		await ctx.send(message)

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("fun")
			#Name of the files inside cogs folder
	#await self.bot.stdout.send("Fun cog ready (test)")
	#print("Fun cog is now ready")



def setup(bot):
	bot.add_cog(Fun(bot))
	#bot.scheduler.add_job(...)