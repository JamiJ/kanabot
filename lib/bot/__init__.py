from discord import Intents
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Embed
from discord.ext.commands import Bot as BotBase

PREFIX ="!"
OWNER_IDS = [137823385404178432]


class Bot(BotBase):
	def __init__(self):
		self.PREFIX = PREFIX
		self.ready = False
		self.guild = None
		self.scheduler = AsyncIOScheduler()



		super().__init__(
			command_prefix=PREFIX, 
			owner_ids=OWNER_IDS
			intents=Intents.all(),
		)

	def run(self, version):
		self.VERSION = version

		with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
			self.TOKEN = tf.read()

		print("running bot...")
		super().run(self.TOKEN, reconnect=True)

	async def on_connect(self):
		print("bot connected")

	async def on_disconnect(self):
		print("bot disconnected")

	async def on_ready(self):
		if not self.ready:
			self.ready = True
			self.guild = self.get_guild(580468127343575175)
			print("bot ready")

			embed = Embed(title="Now online!", description="Kanabot is now live!", color=0xFF0000)
			fields = [("Name", "Value", True),
					  ("Another field", "This is next to the other one.", True),
					  ("A non-inline field", "This field will appear on it's own row.", False)]
			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)
			await channel.send(embed=embed)

		else:
			print("bot reconnected")

	async def on_message(self, message):
		pass

bot = Bot()