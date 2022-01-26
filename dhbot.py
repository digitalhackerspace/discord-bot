import discord
from discord.utils import get
import os
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
	"🎮": 664834183969112065,
	"🔗": 698833505010057229,
	"💸": 703317720774475846,
	"🎙️": 706530739474268170
}
ROLE_ASSIGN_REASON = 'User opted-in to role'

PRIMARY_VOICE_CHANNEL_ID = 565788276859076629
SECONDARY_VOICE_CHANNEL_ID = 854688163943153684

ALIEXPRESS_LINK_REGEX = r" *(?P<protocol>https?:\/\/)?(?P<subdomains>\S*?\.?)(?P<aliLink>aliexpress\.com\/item\/\d*\.html)(?P<queryParameter>\?\S*)?\s*"

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

invites = []
members = []
modlog_channel = None
auto_role = None

@client.event
async def on_ready():
	global invites
	global members
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
			members = await guild.fetch_members(limit=None).flatten()

@client.event
async def on_member_join(member):
	global invites

	for role in member.guild.roles:
		if role.id == AUTO_ROLE_ID:
			await member.add_roles(role, reason=AUTO_ROLE_REASON)
			break

	old_invites = invites.copy()
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

	embed = discord.Embed(title="New User")
	embed.add_field(name="User", value=member.display_name)
	embed.add_field(name="User ID", value=str(member.id))

	found_invite = False
	for i in range(len(invites)):
		if(current_invites[i].uses != invites[i].uses):
			found_invite = True

			embed.add_field(name="Invite Link", value=str(invites[i].id))
			embed.add_field(name="Invite Link Uses", value=str(current_invites[i].uses))
			embed.add_field(name="Inviter", value=invites[i].inviter.display_name)
			embed.add_field(name="Inviter ID", value=str(invites[i].inviter.id))
			break

	if not found_invite:
		possible_invites = list(set(current_invites) - set(old_invites))
		print(str(possible_invites))
		for invite in possible_invites:
			if invite.uses < 1:
				possible_invites.pop(invite)

		print("len_pi=" + str(len(possible_invites)))
		if len(possible_invites) == 1:
			embed.add_field(name="Invite Link", value=str(possible_invites[0].id))
			embed.add_field(name="Invite Link Uses", value=str(possible_invites[0].uses))
			embed.add_field(name="Inviter", value=possible_invites[0].inviter.display_name)
			embed.add_field(name="Inviter ID", value=str(possible_invites[0].inviter.id))
		else:
			i = 0
			for invite in possible_invites:
				embed.add_field(name="Possible Invite Link " + str(i), value="ID: " + str(invite.id) + " Uses: " + str(invite.uses))
				i += 1

	await modlog_channel.send(embed=embed)
	invites = current_invites

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	matches = [m.groupdict() for m in re.finditer(ALIEXPRESS_LINK_REGEX, message.content)]
	matches = [x for x in matches if (x['subdomains'] != "www." and x['subdomains'] != "") or x['queryParameter'] != None]

	if len(matches) > 0:
		embed = discord.Embed(title="Found unclean AliExpress URLs", color=discord.Color.from_rgb(255,0,0))

		i = 0
		for match in matches:
			embed.add_field(name="Url " + str(i), value="https://" + match["aliLink"])
			i += 1

		embed.set_footer(text="Removed the country specific & tracking part from the URL")
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
			user = payload.member
			if user is not None:
				await user.add_roles(role, reason=ROLE_ASSIGN_REASON)
			else:
				print("Error while assigning role by reaction; user is None")

@client.event
async def on_raw_reaction_remove(payload):
	global members

	if payload.message_id != ROLE_ASSIGN_MESSAGE_ID:
		return

	if payload.guild_id is None:
		return

	guild = client.get_guild(payload.guild_id)

	if payload.emoji.is_unicode_emoji():
		if payload.emoji.name in ROLES_TO_ASSIGN:
			role = get(guild.roles, id=ROLES_TO_ASSIGN[payload.emoji.name])
			user = get(members, id=payload.user_id)
			if user is None:
				members = await guild.fetch_members(limit=None).flatten()
				user = get(members, id=payload.user_id)

			if user is not None:
				await user.remove_roles(role, reason=ROLE_ASSIGN_REASON)
			else:
				print("Error while removing role by reaction; user is None")

@client.event
async def on_voice_state_update(member, before, after):
	primary_voice_channel = get(member.guild.voice_channels, id=PRIMARY_VOICE_CHANNEL_ID)
	secondary_voice_channel = get(member.guild.voice_channels, id=SECONDARY_VOICE_CHANNEL_ID)
	is_secondary_voice_channel_public = secondary_voice_channel.overwrites_for(auto_role).connect is True

	if after.channel is None:
		if is_secondary_voice_channel_public and len(secondary_voice_channel.members) == 0 and len(primary_voice_channel.members) == 0:
			await secondary_voice_channel.set_permissions(auto_role, connect=False, view_channel=False)
	else:
		if after.channel.id == PRIMARY_VOICE_CHANNEL_ID and not is_secondary_voice_channel_public:
			await secondary_voice_channel.set_permissions(auto_role, connect=True, view_channel=True)

print("Starting bot...")
client.run(os.environ['DISCORD_TOKEN'])
