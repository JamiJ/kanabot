from asyncio import sleep
from datetime import datetime
from glob import glob
from discord import Intents
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,
								  CommandOnCooldown)
from discord.ext.commands import when_mentioned_or, command, has_permissions

from ..db import db

OWNER_IDS = [137823385404178432]
COGS = [path.split("/")[-1][:-3] for path in glob("./lib/cogs/*.py")]
#If linux / macOS use "/" if Windows use " \\"
#Goes thru this cogs library and adds automatically new files for this list.
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

def get_prefix(bot, message):
	prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
	return when_mentioned_or(prefix)(bot, message)

class Ready(object):
	def __init__(self):
		for cog in COGS:
			setattr(self, cog, False)

	def ready_up(self, cog):
		setattr(self, cog, True)
		print(f" {cog} cog ready")

	def all_ready(self):
		return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
	def __init__(self):
		self.ready = False
		self.cogs_ready = Ready()

		self.guild = None
		self.scheduler = AsyncIOScheduler()

		db.autosave(self.scheduler)
		super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS)
			#intents=Intents.all(), )

	def setup(self):
		for cog in COGS:
			self.load_extension(f"lib.cogs.{cog}")
			print (f" {cog} cog loaded")
			#Prints out the cogs that are loaded

		print("Setup complete")

	def run(self, version):
		self.VERSION = version

		print("running setup...")
		self.setup()

		with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
			self.TOKEN = tf.read()

		print("running bot...")
		super().run(self.TOKEN, reconnect=True)

	async def process_commands(self, message):
		ctx = await self.get_context(message, cls=Context)

		if ctx.command is not None and ctx.guild is not None:
			if self.ready:
				await self.invoke(ctx)

			else:
				await ctx.send("I'm currently not operating correctly. Please wait for a few seconds", delete_after=10)


	async def rules_reminder(self):
		await self.stdout.send("I am a timed notification! Currently posting once a week")
		#sends message every time when self.scheduler.add_job is ran

	async def on_connect(self):
		print("bot connected")

	async def on_disconnect(self):
		print("bot disconnected")

	async def on_error(self, err, *args, **kwargs):
		if err == "on_command_error":
			await args[0].send("Something went wrong.", delete_after=10)

		await self.stdout.send("An error occured.", delete_after=10)
		raise 

	async def on_command_error(self, ctx, exc):
		if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
			pass

		elif isinstance(exc, MissingRequiredArgument):
			await ctx.send("One or more arguments are missing", delete_after=10)

		elif isinstance(exc, CommandOnCooldown):
			await ctx.send(f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in {exc.retry_after:,.2f} secs.", delete_after=20)
			#.split splits the BucketType as it would say "..is on BucketType.XX..
			#With -1 it will get the type and not object name (BucketType)

		elif hasattr(exc, "original"):
				# elif isinstance(exc.original, HTTPException):
				# 		await ctx.send("Unable to send message.")

				if isinstance(exc.original, Forbidden):
					await ctx.send("No permission to do this modification", delete_after=10)

				else:
					raise exc.original

		else:
			raise exc
			

	async def on_ready(self):
		if not self.ready:
			self.guild = self.get_guild(580468127343575175)
			self.stdout = self.get_channel(580468127351963685)
			self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
			#run it every X minute (second="0,15,30,45")
			self.scheduler.start()
			

			
			# embed = Embed(title="Now online!", description="Kanabot is now live!", 
			# 			  color=0xFF0000, timestamp=datetime.utcnow())
			# fields = [("Name", "Value", True),
			# 		  ("Another field", "This is next to the other one.", True),
			# 		  ("A non-inline field", "This field will appear on it's own row.", False)]
			# for name, value, inline in fields:
			# 	embed.add_field(name=name, value=value, inline=inline)
			# 	embed.set_author(name="Kanabot", icon_url=self.guild.icon_url)
			# 	embed.set_footer(text="This is a footer.")
			# await channel.send(embed=embed)

			# #await channel.send(file=File("./data/images/check-mark.png"))

			while not self.cogs_ready.all_ready():
				await sleep(0.5)
			#Waits until every cog is ready.
			
			await self.stdout.send("Up and running!", delete_after=10)
			self.ready = True
			print("bot ready")
		else:
			print("bot reconnected")

	async def on_message(self, message):
		if not message.author.bot:
			await self.process_commands(message)

bot = Bot()