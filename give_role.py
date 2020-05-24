import discord
from discord.utils import get

AUTO_ROLE_ID = 689936291462119506
AUTO_ROLE_REASON = 'Giveaway Auto Role'

GUILD_ID = 565788276397441025

client = discord.Client()

auto_role = None
dh_guild = None

@client.event
async def on_ready():
	global invites
	global modlog_channel
	global auto_role

	print('logged in as {0.user}'.format(client))

	for guild in client.guilds:
		if guild.id == GUILD_ID:
			dh_guild = guild
			for role in guild.roles:
				if role.id == AUTO_ROLE_ID:
					auto_role = role

	for member in guild.members:
		if auto_role not in member.roles:
			await member.add_roles(auto_role, reason=AUTO_ROLE_REASON)
			print("Gave role to " + str(member.display_name))

print("Starting bot...")
client.run('NTY1ODU1MDU1NTUxNTI4OTYw.XK9yGA.ftMNwNZMyWoFxIcFcT8vUWQzhl8')
