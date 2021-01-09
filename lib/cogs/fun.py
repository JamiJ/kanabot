from random import choice, randint
from typing import Optional

from aiohttp import request
from discord import Member, Embed
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument
from discord.ext.commands import command, cooldown


class Fun(Cog):
	def __init__(self, bot):
		self.bot = bot

	#@command(name="test", aliases=["command", "c"], hidden=True)

	@command(name="hello", aliases=["hi"])
	async def say_hello(self, ctx):
		await ctx.send(f"{choice(('Hello', 'Hi', 'Hey'))} {ctx.author.mention}!", delete_after=10)

#	@command(name="dice", aliases=["roll"])
#	async def roll_dice(self, ctx, die_string: str):
#		dice, value = (int(term) for term in die_string.split("d"))
#		rolls = [randint(1, value) for i in range(dice)]
#
#		await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum.(rolls)}")

	@command(name="slap", aliases=["hit"])
	@cooldown(1, 60, BucketType.user)
	#First number is how many times it can be used before cooldown
	#Second number is how long is the cooldown in seconds
	#BucketType.user = user, .
	async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = " for no reason"):
		await ctx.send(f"{ctx.author.display_name} slapped {member.mention} {reason}!", delete_after=10)

	@slap_member.error
	async def slap_member_error(self, ctx, exc):
		if isinstance(exc, BadArgument):
			await ctx.send("Cannot find this member", delete_after=10)

	@command(name="echo", aliases=["say"])
	@cooldown(1, 15, BucketType.guild)
	async def echo_message(self, ctx, *, message):
		await ctx.message.delete()
		await ctx.send(message)

	@command(name="fact")
	@cooldown(3, 60, BucketType.guild)
	async def animal_fact(self, ctx, animal: str):
		if (animal := animal.lower()) in ("dog", "cat", "panda", "fox", "bird", "koala"):
			fact_url = f"https://some-random-api.ml/facts/{animal}"
			image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"

			async with request("GET", image_url, headers={}) as response:
				if response.status == 200:
					data = await response.json()
					image_link = data["link"]
					#coroutine error if this is only in one line
					#image_link = await response.json()["link"]

				else:
					image_link = None

			async with request("GET", fact_url, headers={}) as response:
				if response.status == 200:
					data = await response.json()

					embed = Embed(title=f"{animal.title()} fact",
								  description=data["fact"],
								  color=ctx.author.colour)
					if image_link is not None:
						embed.set_image(url=image_link)
					await ctx.send(embed=embed, delete_after=60)

				else:
					await ctx.send(f"API returned a {response.status} status", delete_after=10)

		else:
			await ctx.send("No facts for that animal. Sorry!..", delete_after=10)


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