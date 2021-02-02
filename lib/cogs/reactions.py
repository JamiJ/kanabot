import discord
import discord.ext.commands
#from discord import Embed, Member
from discord.ext.commands import Cog


class Reactions(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.colours = {
				"❤️": self.bot.guild.get_role(806192853965078618), #Red not working? might be related to the editor i'm using
				"🧡": self.bot.guild.get_role(806192795948941333), #Orange
				"💛": self.bot.guild.get_role(806192602051248178), #Yellow
				"💚": self.bot.guild.get_role(806192641904476180), #Green
				"💙": self.bot.guild.get_role(806193217506639922), #Blue
				"💜": self.bot.guild.get_role(806192720645193749), #Purple
				"🖤": self.bot.guild.get_role(806192662323265546), #Black
				"🤎": self.bot.guild.get_role(806193048764809323), #Brown
				"🤍": self.bot.guild.get_role(806192853965078618), #White
			}
			self.reaction_message = await self.bot.get_channel(580468127351963685).fetch_message(806190845246177301)
			#If message / channel is removed / moved this will error 
			self.bot.cogs_ready.ready_up("reactions")

#	@Cog.listener()
#	async def on_reaction_add(self, reaction, user):
#		print(f"{user.display_name} reacted with {reaction.emoji}")
#
#	@Cog.listener()
#	async def on_reaction_remove(self, reaction, user):
#		print(f"{user.display_name} removed the reaction of {reaction.emoji.name}")

	@Cog.listener()
	async def on_raw_reaction_add(self, payload):
		#print(f"[RAW] {payload.member.display_name} reacted with {payload.emoji.name}")
		if self.bot.ready and payload.message_id == self.reaction_message.id:
			current_colours = filter(lambda r: r in self.colours.values(), payload.member.roles)
			await payload.member.remove_roles(*current_colours, reason="Colour role reaction.")
			await payload.member.add_roles(self.colours[payload.emoji.name], reason="Colour role reaction.")
			await self.reaction_message.remove_reaction(payload.emoji, payload.member)

#	@Cog.listener()
#	async def on_raw_reaction_remove(self, payload):
#		
#		#print(f"[RAW] {member.display_name} removed the reaction of {payload.emoji.name}")
#		if self.bot.ready and payload.message_id == self.reaction_message.id:
#			print(payload.user_id)
#			print(self.bot.guild.id)
#			print(self.bot.guild.get_member(int(payload.user_id)))
#			member = self.bot.guild.get_member(int(payload.user_id))
#			#role = self.bot.guild.get_role(colours[payload.emoji.name])
#			await member.remove_roles(self.colours[payload.emoji.name], reason="Colour role reaction.")
#		#doesn't work
		


def setup(bot):
	bot.add_cog(Reactions(bot))