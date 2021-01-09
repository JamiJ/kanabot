from asyncio import sleep
from datetime import datetime, timedelta
from re import search
from typing import Optional

from better_profanity import profanity
#will check if words are being used numbers and different special characters.
from discord import Embed, Member, NotFound, Object
from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure, BadArgument
from discord.ext.commands import command, has_permissions, bot_has_permissions

from ..db import db

profanity.load_censor_words_from_file("./data/profanity.txt")

class Mod(Cog):
	def __init__(self, bot):
		self.bot = bot

		self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
		#checks the link that it is valid
		self.links_allowed = (580468127351963685, 580508887413686289)
		self.images_allowed = (580468127351963685, 580508887413686289)


	async def kick_membners(self, message, targets, reason):
		for target in targets:
			if (message.guild.me.top_role.position > target.top_role.position 
				and not target.guild_permissions.administrator):
				#This checks that the role of the bot is higher than the role of the target and not administrator
				await target.kick(reason=reason)

				embed = Embed(title="Member kicked",
							  colour=0xDD2222,
							  timestamp=datetime.utcnow())

				embed.set_thumbnail(url=target.avatar_url)

				fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
						  ("Actioned by", message.author.display_name, False),
						  ("Reason", reason, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				await self.log_channel.send(embed=embed)

	@command(name="kick", brief="Kick member from the server.")
	@bot_has_permissions(kick_members=True)
	@has_permissions(kick_members=True)
	async def kick_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("One or more arguments are missing", delete_after=10)

		else:
			await self.kick_members(ctx.message, targets, reason)
			await ctx.send("Action complete.", delete_after=10)

	@kick_command.error
	async def kick_command_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("Insufficient permissions to perform that task.")

	async def ban_members(self, message, targets, reason):
		for target in targets:
				if (message.guild.me.top_role.position > target.top_role.position 
				and not target.guild_permissions.administrator):
				#This checks that the role of the bot is higher than the role of the target and not administrator
					await target.ban(reason=reason)

					embed = Embed(title="Member banned",
								  colour=0xDD2222,
								 timestamp=datetime.utcnow())

					embed.set_thumbnail(url=target.avatar_url)

					fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
							  ("Actioned by", message.author.display_name, False),
							  ("Reason", reason, False)]

					for name, value, inline in fields:
						embed.add_field(name=name, value=value, inline=inline)

					await self.log_channel.send(embed=embed)

	@command(name="ban", brief="Ban member from the server.")
	@bot_has_permissions(ban_members=True)
	@has_permissions(ban_members=True)
	async def ban_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("One or more arguments are missing", delete_after=10)

		else:
			#await ctx.send(f"{target.display_name} could not be banned.")
			await self.ban_members(ctx.message, targets, reason)
			await ctx.send("Action complete.", delete_after=10)

	@ban_command.error
	async def ban_command_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("Insufficient permissions to perform that task.")

	@command(name="clear", aliases=["purge"], brief="Clear chat @User X times.")
	@bot_has_permissions(manage_messages=True)
	@has_permissions(manage_messages=True)
	async def clear_messages(self, ctx, targets: Greedy[Member], limit: Optional[int] = 1):
		def _check(message):
			return not len(targets) or message.author in targets
		#If you add example @user it will delete the latest X(how many) messages from @user
		#NOTE every message in X will be counted, even if it's not from @user. It will skip those 
		#but these does count to the X you have given.

		if 0 < limit <= 100:
			with ctx.channel.typing():
				await ctx.message.delete()
				deleted = await ctx.channel.purge(limit=limit, after=datetime.utcnow()-timedelta(days=14), 
												  check=_check)
				#timedelta will allow to only delete messages that are in 14 days range, no older messages will be removed

				await ctx.send(f"Deleted {len(deleted):,} messages.", delete_after=5)

		else:
			await ctx.send("The limit provided is not within acceptable bounds.", delete_after=10)


	async def mute_members(self, message, targets, hours, reason):
		unmutes = []

		for target in targets:
			if not self.mute_role in target.roles:
				if message.guild.me.top_role.position > target.top_role.position:
					role_ids =",".join([str(r.id) for r in target.roles])
					end_time = datetime.utcnow() + timedelta(seconds=hours) if hours else None
					#timedelta(seconds=hours*3600)

					db.execute("INSERT INTO mutes VALUES (?, ?, ?)",
								target.id, role_ids, getattr(end_time, "isoformat", lambda: None)())

					await target.edit(roles=[self.mute_role])

					embed = Embed(title="Member muted",
								  colour=0xDD2222,
								 timestamp=datetime.utcnow())

					embed.set_thumbnail(url=target.avatar_url)

					fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
							  ("Actioned by", message.author.display_name, False),
							  ("Duration", f"{hours:,} hour(s)" if hours else "Indefinite", False),
							  ("Reason", reason, False)]

					for name, value, inline in fields:
						embed.add_field(name=name, value=value, inline=inline)

					await self.log_channel.send(embed=embed)

					if hours:
						unmutes.append(target)

		return unmutes

	#This needs to be tested much better also unmute command
	#some secret stuff is still happening, please try with normal people, not bots.
	#somtimes dont spam mentions triggers, even no mentios is showed
	@command(name="mute", brief="Mute member for X hours.")
	@bot_has_permissions(manage_roles=True)
	@has_permissions(manage_roles=True, manage_guild=True)
	async def mute_command(self, ctx, targets: Greedy[Member], hours: Optional[int], *,
						   reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("One or more required arguments are missing.")

		else:
			unmutes = await self.mute_members(ctx.message, targets, hours, reason)
			await ctx.send("Action complete.", delete_after=10)

			if len(unmutes):
				await sleep(hours)
				await self.unmute_members(ctx.guild, targets)

	@mute_command.error
	async def mute_command_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("Insufficient permissions to perform that task.")

	async def unmute_members(self, guild, targets, *, reason="Mute time expired."):
		for target in targets:
			if self.mute_role in target.roles:
				role_ids = db.field("SELECT RoleIds FROM mutes WHERE UserID = ?", target.id)
				roles = [guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

				db.execute("DELETE FROM mutes WHERE UserID = ?", target.id)

				await target.edit(roles=roles)

				embed = Embed(title="Member unmuted",
							  colour=0xDD2222,
							  timestamp=datetime.utcnow())

				embed.set_thumbnail(url=target.avatar_url)

				fields = [("Member", f"{target.display_name}", False),
						  ("Reason", reason, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				await self.log_channel.send(embed=embed)

	@command(name="unmute", brief="Unmute member.")
	@bot_has_permissions(manage_roles=True)
	@has_permissions(manage_roles=True, manage_guild=True)
	async def unmute_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("One or more required arguments is missing.", delete_after=10)

		else:
			await self.unmute_members(ctx.guild, targets, reason=reason)

	@command(name="addprofanity", aliases=["addswears", "addcursers"], brief="Add words to profanity filter.")
	@has_permissions(manage_guild=True)
	async def add_profanity(self, ctx, *words):
		with open("./data/profanity.txt", "a", encoding="utf-8") as f:
			f.write("".join([f"{w}\n" for w in words]))

		profanity.load_censor_words_from_file("./data/profanity.txt")
		#this word is added immediately when you hit !addprofanity X
		#and it will show as notification about "You can't use that word..."
		#this needs to be fixed later on
		#maybe to use aiofiles?
		await ctx.send("Action complete.", delete_after=10)

	@command(name="delprofanity", aliases=["delswears", "delcurses"], brief="Delete words from profanity filter.")
	@has_permissions(manage_guild=True)
	async def remove_profanity(self, ctx, *words):
		with open("./data/profanity.txt", "r", encoding="utf-8") as f:
			stored = [w.strip() for w  in f.readlines()]

		with open("./data/profanity.txt", "w", encoding="utf-8") as f:
			f.write("".join([f"{w}\n" for w in stored if w not in words]))

		profanity.load_censor_words_from_file("./data/profanity.txt")
		await ctx.send("Action complete.", delete_after=10)

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.log_channel = self.bot.get_channel(580508887413686289)
			self.mute_role = self.bot.guild.get_role(794297980403449917)
			self.bot.cogs_ready.ready_up("mod")

	@Cog.listener()
	async def on_message(self, message):
		def _check(m):
			return (m.author == message.author
							and len(m.mentions)
							and (datetime.utcnow()-m.created_at).seconds < 60)

		if not message.author.bot:
			if len(list(filter(lambda m: _check(m), self.bot.cached_messages))) >= 3:
				await message.channel.send("Don't spam mentions!", delete_after=10)
				unmutes = await self.mute_members(message, [message.author], 1, reason="Mention spam")

				if len(unmutes):
					await sleep(5)
					await self.unmute_members(message.guild, [message.author])

			elif profanity.contains_profanity(message.content):
				await message.delete()
				await message.channel.send("You can't use that word. It's automatically removed.", delete_after=10)

			elif message.channel.id not in self.links_allowed and search(self.url_regex, message.content):
				await message.delete()
				await message.channel.send("You can't send link in this channel.", delete_after=10)

			elif (message.channel.id not in self.images_allowed
				and any([hasattr(a, "width") for a in message.attachments])):
				await message.delete()
				await message.channel.send("You can't send images here.", delete_after=10)
				#this is sending an error because of the link check. Needs to be adjusted




def setup(bot):
	bot.add_cog(Mod(bot))