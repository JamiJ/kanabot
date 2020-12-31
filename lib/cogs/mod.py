from asyncio import sleep
from datetime import datetime, timedelta
from typing import Optional

from discord import Embed, Member
from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions, bot_has_permissions

from ..db import db

class Mod(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="kick")
	@bot_has_permissions(kick_members=True)
	@has_permissions(kick_members=True)
	async def kick_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("One or more arguments are missing", delete_after=10)

		else:
			for target in targets:
				if (ctx.guild.me.top_role.position > target.top_role.position 
					and not target.guild_permissions.administrator):
				#This checks that the role of the bot is higher than the role of the target and not administrator
					await target.kick(reason=reason)

					embed = Embed(title="Member kicked",
								  colour=0xDD2222,
								 timestamp=datetime.utcnow())

					embed.set_thumbnail(url=target.avatar_url)

					fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
							  ("Actioned by", ctx.author.display_name, False),
							  ("Reason", reason, False)]

					for name, value, inline in fields:
						embed.add_field(name=name, value=value, inline=inline)

					await self.log_channel.send(embed=embed)

				else:
					await ctx.send(f"{target.display_name} could not be kicked.")

			await ctx.send("Action complete.")

	@kick_members.error
	async def kick_members_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("Insufficient permissions to perform that task.")

	@command(name="ban")
	@bot_has_permissions(ban_members=True)
	@has_permissions(ban_members=True)
	async def ban_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("One or more arguments are missing", delete_after=10)

		else:
			for target in targets:
				if (ctx.guild.me.top_role.position > target.top_role.position 
				and not target.guild_permissions.administrator):
				#This checks that the role of the bot is higher than the role of the target and not administrator
					await target.ban(reason=reason)

					embed = Embed(title="Member banned",
								  colour=0xDD2222,
								 timestamp=datetime.utcnow())

					embed.set_thumbnail(url=target.avatar_url)

					fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
							  ("Actioned by", ctx.author.display_name, False),
							  ("Reason", reason, False)]

					for name, value, inline in fields:
						embed.add_field(name=name, value=value, inline=inline)

					await self.log_channel.send(embed=embed)

				else:
					await ctx.send(f"{target.display_name} could not be banned.")

			await ctx.send("Action complete.")

	@ban_members.error
	async def ban_members_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("Insufficient permissions to perform that task.")

	@command(name="clear", aliases=["purge"])
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
			await ctx.send("The limit provided is not within acceptable bounds.")


	#This needs to be tested much better also unmute command
	@command(name="mute")
	@bot_has_permissions(manage_roles=True)
	@has_permissions(manage_roles=True, manage_guild=True)
	async def mute_members(self, ctx, targets: Greedy[Member], hours: Optional[int], *,
						   reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("Insufficient permissions to perform that task.")

		else:
			unmutes = []

			for target in targets:
				if not self.mute_role in target.roles:
					if ctx.guild.me.top_role.position > target.top_role.position:
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
								  ("Actioned by", ctx.author.display_name, False),
								  ("Duration", f"{hours:,} hour(s)" if hours else "Indefinite", False),
								  ("Reason", reason, False)]

						for name, value, inline in fields:
							embed.add_field(name=name, value=value, inline=inline)

						await self.log_channel.send(embed=embed)

						if hours:
							unmutes.append(target)

					else:
						await ctx.send(f"{target.display_name} could not be muted.")

				else:
					await ctx.send(f"{target.display_name} is already muted.")

			await ctx.send("Action complete.")

			if len(unmutes):
				await sleep(hours)
				await self.unmute(ctx, targets)

	@mute_members.error
	async def mute_members_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("Insufficient permissions to perform that task.")

	async def unmute(self, ctx, targets, *, reason="Mute time expired."):
		for target in targets:
			if self.mute_role in target_roles:
				role_ids = db.field("SELECT RoleIds FROM mutes WHERE UserID = ?", target.id)
				roles = [ctx.guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

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

	@command(name="unmute")
	@bot_has_permissions(manage_roles=True)
	@has_permissions(manage_roles=True, manage_guild=True)
	async def unmute_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("One or more required arguments is missing.")

		else:
			await self.unmute(ctx, targets, reason=reason)





	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.log_channel = self.bot.get_channel(580508887413686289)
			self.mute_role = self.bot.guild.get_role(794297980403449917)
			self.bot.cogs_ready.ready_up("mod")


def setup(bot):
	bot.add_cog(Mod(bot))