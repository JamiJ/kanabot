from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions

from ..db import db

def to_ascii(string):
	string = string.replace("ä", "/ae").replace("ö", "/oe").replace("Ä", "/AE").replace("Ö", "/OE").replace("§", "/ss")
	return string
			
def to_utf8(string):
	string = string.replace("Ã¤", "ä").replace("Ã¶", "ö").replace("/ae", "ä").replace("/oe", "ö").replace("Ã„", "Ä") \
		.replace("Ã–", "Ö").replace("Â§", "§").replace("/ss", "§").replace("/AE", "Ä").replace("Ö", "/OE")
	return string

class Customgroup(Cog):
	def __init__(self, bot):
		self.bot = bot




	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("Customgroup")


def setup(bot):
	bot.add_cog(Customgroup(bot))