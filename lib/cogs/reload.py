from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions


class Reload(Cog):
	def __init__(self, bot):
		self.bot = bot    
	
	
	@command(name="reload", brief="Reloads an extension.")
	async def reload(self, ctx, name: str):
		"""Reloads an extension."""
		if ctx.author.id == 137823385404178432:
			try:
				self.bot.reload_extension(f"lib.cogs.{name}")
				await ctx.send(f"Reloaded extension **{name}.py**", delete_after=60)
				print(f"Reloaded extension {name}.py")
			except Exception as e:
				print(e)
				await ctx.send("Invalid filename.", delete_after=10)
	
		else:
			await ctx.send("You do not have permissions to perform this command.", delete_after=10)

	@command(name="unload", brief="Unloads an extension.")
	async def unload(self, ctx, name: str):
		"""Unloads an extension."""
		if ctx.author.id == 137823385404178432:
			try:
				self.bot.unload_extension(f"lib.cogs.{name}")
				await ctx.send(f"Unloaded extension **{name}.py**", delete_after=60)
				print(f"Unloaded extension {name}.py")
			except Exception as e:
				print(e)
				await ctx.send("Invalid filename.", delete_after=10)
	
		else:
			await ctx.send("You do not have permissions to perform this command.", delete_after=10)

	@command(name="load", brief="Loads an extension.")
	async def load(self, ctx, name: str):
		"""Loads an extension."""
		if ctx.author.id == 137823385404178432:
			try:
				self.bot.load_extension(f"lib.cogs.{name}")
				await ctx.send(f"Loaded extension **{name}.py**", delete_after=60)
				print(f"Loaded extension {name}.py")
			except Exception as e:
				print(e)
				await ctx.send("Invalid filename.", delete_after=10)
	
		else:
			await ctx.send("You do not have permissions to perform this command.", delete_after=10)
	

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("reload")


def setup(bot):
	bot.add_cog(Reload(bot))