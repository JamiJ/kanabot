from discord import Forbidden
from discord.ext.commands import Cog
from discord.ext.commands import command

from ..db import db

class Members(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("members")

	@Cog.listener()
	async def on_member_join(self, member):
		db.execute("INSERT INTO exp (UserID) VALUES (?)", member.id)
		await self.bot.get_channel(789597833820373002).send(f"Welcome to **{member.guild.name}** {member.mention}!")

		#Trying to send DM message if that is what is wanted and will pass if DM's on user is turned off.
		#try:
			#await member.send(f"Welcome to **{member.guild.name}**! Enjoy your stay!")

		#except Forbidden:
			#pass


		await member.add_roles(*(member.guild.get_role(id_) for id_ in (580498110988419072, 627868064863485962)))
		#adds new roles back to back, and not overwriting the first role (hardcoded)

	@Cog.listener()
	async def on_member_remove(self, member):
		db.execute("DELETE FROM exp WHERE UserID = ?", member.id)
		await self.bot.get_channel(789597857295761421).send(f"{member.display_name} has left {member.guild.name}.")


def setup(bot):
	bot.add_cog(Members(bot))