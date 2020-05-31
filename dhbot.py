import discord
from discord.utils import get
import re

AUTO_ROLE_ID = 565793207338926080
AUTO_ROLE_REASON = 'Join Auto Role'

MODLOG_CHANNEL_ID = 582114965662597149

GUILD_ID = 565788276397441025

ROLE_ASSIGN_MESSAGE_ID = 607960633975111680
ROLES_TO_ASSIGN = {
	"🇲": 607966216430026755,
	"🕵": 610777018501431296,
	"🇳": 607969679377694721,
	"🇸": 608030866030985256,
	"🇦": 608030909303750843,
	"🌍": 608030940706504805,
	"🌊": 608033299582943253,
	"🇪🇺": 607969641087893506,
	"🇩": 607969662096900116,
	"📡": 612387232149536848,
	#"🚀": 631118646223306782, - 36c3 is over
	#"😋": 669969087501303828, - Made snackhacks public
	"🎮": 664834183969112065,
	"🔗": 698833505010057229,
	"💸": 703317720774475846,
	"🎙️": 706530739474268170
}
ROLE_ASSIGN_REASON = 'User opted-in to role'

ALIEXPRESS_LINK_REGEX = r"\.(aliexpress\.com\/item\/.*\.html)"

client = discord.Client()

invites = []
modlog_channel = None
auto_role = None

@client.event
async def on_ready():
	global invites
	global modlog_channel
	global auto_role

	print('logged in as {0.user}'.format(client))
	
	for guild in client.guilds:
		if guild.id == GUILD_ID:
			for channel in guild.text_channels:
				if channel.id == MODLOG_CHANNEL_ID:
					modlog_channel = channel
			for role in guild.roles:
				if role.id == AUTO_ROLE_ID:
					auto_role = role

			invites = await guild.invites()

@client.event
async def on_member_join(member):
	global invites

	for role in member.guild.roles:
		if role.id == AUTO_ROLE_ID:
			await member.add_roles(role, reason=AUTO_ROLE_REASON)
			break

	current_invites = await member.guild.invites()

	if len(current_invites) > len(invites):
		for invite in current_invites:
			if invite not in invites:
				invites.append(invite)

	if len(current_invites) < len(invites):
		for invite in invites:
			if invite not in current_invites:
				invites.remove(invite)

	current_invites.sort(key=lambda x: x.created_at)
	invites.sort(key=lambda x: x.created_at)

	for i in range(len(invites)):
		if(current_invites[i].uses != invites[i].uses):
			embed = discord.Embed(title="New User")

			embed.add_field(name="User", value=member.display_name)
			embed.add_field(name="User ID", value=str(member.id))
			embed.add_field(name="Invite Link", value=str(invites[i].id))
			embed.add_field(name="Invite Link Uses", value=str(current_invites[i].uses))
			embed.add_field(name="Inviter", value=invites[i].inviter.display_name)
			embed.add_field(name="Inviter ID", value=str(invites[i].inviter.id))

			await modlog_channel.send(embed=embed)
			break

	invites = current_invites

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	matches = re.findall(ALIEXPRESS_LINK_REGEX, message.content)
	if matches is not None:
		embed = discord.Embed(title="Found unclean AliExpress URLs", color=discord.Color.from_rgb(255,0,0))
		
		i = 0
		for match in matches:
			embed.add_field(name="Url " + str(i), value="https://" + match)
			i += 1

		await message.channel.send(embed=embed)

@client.event
async def on_raw_reaction_add(payload):
	# print(payload.emoji.name)

	if payload.message_id != ROLE_ASSIGN_MESSAGE_ID:
		return

	if payload.guild_id is None:
		return

	guild = client.get_guild(payload.guild_id)
	
	if payload.emoji.is_unicode_emoji():
		if payload.emoji.name in ROLES_TO_ASSIGN:
			role = get(guild.roles, id=ROLES_TO_ASSIGN[payload.emoji.name])
			user = get(guild.members, id=payload.user_id)
			if user is not None:
				await user.add_roles(role, reason=ROLE_ASSIGN_REASON)
			else:
				print("Error while assigning role by reaction; user is None")


@client.event
async def on_raw_reaction_remove(payload):
	if payload.message_id != ROLE_ASSIGN_MESSAGE_ID:
		return

	if payload.guild_id is None:
		return

	guild = client.get_guild(payload.guild_id)
	
	if payload.emoji.is_unicode_emoji():
		if payload.emoji.name in ROLES_TO_ASSIGN:
			role = get(guild.roles, id=ROLES_TO_ASSIGN[payload.emoji.name])
			user = get(guild.members, id=payload.user_id)
			if user is not None:
				await user.remove_roles(role, reason=ROLE_ASSIGN_REASON)
			else:
				print("Error while assigning role by reaction; user is None")

print("Starting bot...")
client.run('NTY1ODU1MDU1NTUxNTI4OTYw.XK9yGA.ftMNwNZMyWoFxIcFcT8vUWQzhl8')
