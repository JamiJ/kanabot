from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions

from ..db import db

class Misc(Cog):
	def __init__(self, bot):
		self.bot = bot


	@command(name="prefix", brief="Change bot prefix in current server.")
	@has_permissions(manage_guild=True)
	async def change_prefix(self, ctx, new: str):
		if len(new) > 5:
			await ctx.send("The prefix can not be more than 5 characters in lenght.", delete_after=10)

		else:
			db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, ctx.guild.id)
			#make it so it automatically adds the new GuildID when this command is given.
			#currently you need to manually add the guild into database
			await ctx.send(f"Prefix set to {new}.", delete_after=60)

	@change_prefix.error
	async def change_prefix_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("You need the Manage Server permission to do that.", delete_after=10)
			#basic error handling for missing permissions

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("misc")


def setup(bot):
	bot.add_cog(Misc(bot))