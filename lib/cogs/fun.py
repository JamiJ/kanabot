from discord.ext.commands import Cog

class Fun(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("fun")
			#Name of the files
	#await self.bot.stdout.send("Fun cog ready (test)")
	#print("Fun cog is now ready")



def setup(bot):
	bot.add_cog(Fun(bot))
	#bot.scheduler.add_job(...)