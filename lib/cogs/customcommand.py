from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions, group
from discord.ext import commands
import os
import sys
import io
import json

from ..db import db

def to_ascii(string):
	string = string.replace("ä", "/ae").replace("ö", "/oe").replace("Ä", "/AE").replace("Ö", "/OE").replace("§", "/ss")
	return string
			
def to_utf8(string):
	string = string.replace("Ã¤", "ä").replace("Ã¶", "ö").replace("/ae", "ä").replace("/oe", "ö").replace("Ã„", "Ä") \
		.replace("Ã–", "Ö").replace("Â§", "§").replace("/ss", "§").replace("/AE", "Ä").replace("Ö", "/OE")
	return string

class Customcommand(Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(name="command")#, pass_context=True
	async def _command(self, ctx):
		""" Tell users what your group command is all about here"""
		if ctx.invoked_subcommand is None:
			print ("Command given whitout subcommand")
			await ctx.send("`!command add/edit/remove hi ""\"hello""\"`", delete_after=30.0)
			await ctx.message.delete()

	#listeners now must have a decorator
	@commands.Cog.listener()
	async def on_message(self, message):
		guild = message.guild
		channel = message.channel
		user = message.author
		path = "./data/custom/".format(os.path.dirname(__file__))
		if path == "/":
			path = ""
		voice = "./data/custom/".format(os.path.dirname(__file__))
		if voice == "/":
			voice = ""
		try:
			if message.content.startswith('!'):
				#channel = message.channel
				#await channel.send(f'Kirjoitit , {message.content}')
				if guild:
					with open("{}chatlogs/{}.txt".format(path, guild.name), "a+", encoding="utf-8") as logs:
						print(to_utf8(str(("{0.created_at} : {0.author.name} : {0.channel} : {0.content} : {0.embeds}".format(message)))), file=logs)
				try:
					server = message.guild.id
				except AttributeError:
					return
				command = message.content.replace("!", "")
				#print (command)
				try:
					with open(f"{path}custom_commands.json") as data_file:
						data = json.load(data_file)
						#print("Tiedosto avattu")
					try:
						viesti = data[str(server)]["!{}".format(to_ascii(str(command)))]["message"]
						await channel.send(to_utf8(viesti), delete_after=300.0)
						#await message.message.delete()
						print(user)
						return
					except KeyError: #NameError for fixing, if command manage is broken
						return
						print("Unable to deliver message (KeyError). Path is wrong")
				except IOError:
					print ("Problems with opening file. Path is wrong")
					return
			else:
				#print("Viesti ei alkanut '!' merkillä")
				#print("Poistetaan käyttäjän lähettämä viesti")
				#await self.message.delete()
				#await bot.process_commands(message)
				pass
				#return
		except AttributeError:
			#print("Komento aloitettiin väärin!")
			pass
		
		
	#@commands.command(name='command-add', aliases=['lisaa'])
	@_command.command()
	@commands.guild_only()
	@commands.has_any_role("Admins")
	async def add(self, message, *, arg):
		path = "{}/customfiles/".format(os.path.dirname(__file__))
		if path == "/":
			path = ""
		words = "".join(arg)#.replace(" ", " ")	
		file = f"{path}custom_commands.json"
		#channel = message.guild.get_channel(521118811198586891)
		channel = message.channel
		server = message.guild.id
		
		if len(words) < 3:
			await channel.send("Please give a command and a message for it: `!command add hi ""\"hello""\"`", delete_after=40.0)
			#await channel.send(f"{arg}")
			return
			
		def convert(string):
			a = string.find("\"")
			if a == -1 or string[-1] != "\"" or string.count("\"") < 2:
				return
			string_list = list(string)
			string_list[a], string_list[-1] = "[start]", "[end]"
			if string_list[a - 1] != " ":
				string_list[a - 1] += " "
			string = "".join(string_list)
			start = string.find("[start]") + 7
			end = string.find("[end]")
			viesti_raw = to_ascii(string[start:end]).replace("\\n", "\n")
			komento_raw = to_ascii(" ".join(string[:start - 8].split(" ")[0:]))
			komento = komento_raw.replace("!", "")
			try:
				if not komento[0].isalpha() and not komento[0].isdigit():
					komento = list(komento)
					komento[0] = "!"
					komento = "".join(komento)
				elif komento[0].isalpha() or komento[0].isdigit():
					komento = "!" + komento
				return komento.lower(), viesti_raw, komento_raw
			except IndexError:
				raise IndexError
		try:
			command, viesti, command_raw = convert(words)
			if len(command_raw) > 30:
				raise ValueError
			if "[end]" in command and "[start]" in command:
				await channel.send("Please give first command and then message between "
														   "quotation marks.", delete_after=40.0)
				await message.message.delete()
				return
		except TypeError:
			await channel.send("Message of the command has to begin and end to "
													   "quotation mark. "
													   "`!command add hi ""\"hello""\"`", delete_after=40.0)
			await message.message.delete()
			return
		except IndexError:
			await channel.send("Command name cannot be only prefixes, "
													   "as they will be removed when command is added.", delete_after=40.0)
			await message.message.delete()
			return
		except ValueError:
			await channel.send(f"Command max length is 30 characters. Yours was: "f"{len(command_raw)}.", delete_after=30.0)
			await message.message.delete()
			return
		with open(file) as data_file:
			data = json.load(data_file)
		try:
			server_commands = list(data[str(server)])
			if command in server_commands:
				await channel.send("This command already exists.", delete_after=40.0)
				await message.message.delete()
				return
			elif len(server_commands) > 1999:
				await channel.send("Komentojen maksimimäärä on 1999 kappaletta, joka on tällä "
														   "guildilla jo täyttynyt.", delete_after=40.0)
				await message.message.delete()
				return
		except KeyError:
			data[str(server)] = {}
		data[str(server)][command] = {"message": viesti}
		with open(file, "w") as data_file:
			json.dump(data, data_file, indent=4)
		await channel.send("Command `{}` added.".format(to_utf8(command)), delete_after=40.0)
		await message.message.delete()
		if (command_raw[0] == "!" and command_raw.count("!") > 1) or (command_raw[0] != "!" and command_raw.count("!") > 0):
			#await channel.send("Komennon nimessä ei voi olla huutomerkkejä ja ne poistettiin automaattisesti.")
			print ("Komennon nimessä ei voi olla huutomerkkejä ja ne poistettiin automaattisesti.")

	#@commands.command(name='command-del', aliases=['poista', 'remove'])
	@_command.command()
	@commands.guild_only()
	@commands.has_any_role("Admins")
	async def remove(self, message, *, arg):
		#channel = message.guild.get_channel(521118811198586891)
		channel = message.channel
		komento = " ".join(arg).replace(" ", "")
		server = message.guild.id
		path = "{}/data/custom/".format(os.path.dirname(__file__))
		if path == "/":
			path = ""
		file = f"{path}custom_commands.json"
		if not komento[0].isalpha() and not komento[0].isdigit():
			komento = list(komento)
			komento[0] = "!"
			komento = "".join(komento)
		elif komento[0].isalpha() or komento[0].isdigit():
			komento = "!" + komento
		komento = to_ascii(komento)
		with open(file) as data_file:
			data = json.load(data_file)
		if str(komento) in list(data[str(server)]):
			del data[str(server)][str(komento)]
			with open(file, "w") as data_file:
				json.dump(data, data_file, indent=4)
				await channel.send("Command `{}` removed.".format(to_utf8(str(komento))), delete_after=40.0)
				await message.message.delete()
		else:
			await channel.send(f"Command: `{arg}` doesn't exist.", delete_after=40.0)
			await message.message.delete()
			
	#@commands.command(name='command-del', aliases=['poista', 'remove'])
	@_command.command()
	@commands.guild_only()
	@commands.has_any_role("Admins")
	async def edit(self, message, *, arg): 	#(self, message, words_raw):
		channel = message.channel
		#komento = " ".join(arg)#.replace(" ", "")
		server = message.guild.id
		path = "{}/data/custom/".format(os.path.dirname(__file__))
		if path == "/":
			path = ""
		file = f"{path}custom_commands.json"
		words = " ".join(arg).replace(" ", "")

		with open(file) as data_file:
			data = json.load(data_file)
		def convert(string):
			a = string.find("\"")
			if a == -1 or string[-1] != "\"" or string.count("\"") < 2:
				return
			string_list = list(string)
			string_list[a], string_list[-1] = "[start]", "[end]"
			if string_list[a - 1] != " ":
				string_list[a - 1] += " "
			string = "".join(string_list)
			start = string.find("[start]") + 7
			end = string.find("[end]")
			viesti_raw = to_ascii(string[start:end]).replace("\\n", "\n")
			komento = to_ascii(" ".join(string[:start - 8].split(" ")[0:])).replace("!", "")
			if not komento[0].isalpha() and not komento[0].isdigit():
				komento = list(komento)
				komento[0] = "!"
				komento = "".join(komento)
			elif komento[0].isalpha() or komento[0].isdigit():
				komento = "!" + komento
			return komento.lower(), viesti_raw

		try:
			command, viesti_edited = convert(words)
		except TypeError:
			await channel.send("Message of the command has to begin and end to a quotation mark.", delete_after=40.0)
			await message.message.delete()
			return
		try:
			if str(command) in list(data[str(server)]):
				old_message = data[str(server)][str(command)]["message"]
				if viesti_edited != old_message:
					data[str(server)][str(command)]["message"] = viesti_edited
				else:
					await channel.send("New message cannot be the same as old one.", delete_after=40.0)
					await message.message.delete()
					return
			else:
				await channel.send("Command given doesn't exists.", delete_after=40.0)
				await message.message.delete()
				return
		except KeyError:
			await channel.send("Server doesn't have commands enabled.", delete_after=40.0)
			await message.message.delete()
			return
		with open(file, "w") as data_file:
			json.dump(data, data_file, indent=4)
		await channel.send("Modified command: `{}`.".format(command), delete_after=40.0)
		await message.message.delete()
		
	#@commands.command(name='command-del', aliases=['poista', 'remove'])
	@_command.command()
	@commands.guild_only()
	@commands.has_any_role("Admins")
	async def check(self, message):#, *, arg
		#channel = message.guild.get_channel(521118811198586891)
		channel = message.channel
		#komento = " ".join(arg).replace(" ", "")
		server = message.guild.id
		path = "{}/data/custom/".format(os.path.dirname(__file__))
		if path == "/":
			path = ""
		file = f"{path}custom_commands.json"
		
		with open(file, 'r') as data_file:
			data = json.load(data_file)
		
		#commandsall = data["236863812651843584"]
		commandsall = data[f"{server}"]
		
		#print (data["236863812651843584"])
		await channel.send(f"```json \n Servers commands: \n{commandsall}```", delete_after=200.0)#.format(commands)

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("Customcommand")


def setup(bot):
	bot.add_cog(Customcommand(bot))