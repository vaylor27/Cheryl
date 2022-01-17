import json
import discord
from discord import guild
from discord.ext import commands
import random


def get_prefix(client, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]


client = commands.Bot(command_prefix=get_prefix)


@client.event
async def on_ready():
    print("Cheryl is back online")


@client.event
async def on_guild_join(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = "-"

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f)


@client.command(aliases=['prefix?', 'Prefix?', '@Cheryl#3984s'])
async def on_message(msg):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    pre = prefixes[str(msg.guild.id)]

    await msg.channel.send(f'Hello@' + {msg.author} + f'I am Cheryl, a bot made by James. My prefix is {pre}')


@client.command(aliases=['p', 'pi', 'Ping', 'P', 'Pi', 'PI', 'pI'])
async def ping(ctx):
    await ctx.send('Pong!')


@client.command(aliases=['prefix', 'Changeprefix', 'Prefix'])
async def changeprefix(ctx, prefix):
    if not ctx.author.guild_permissions.manage_channels:
        ctx.send(f'LOL!, @{ctx.author} does not have manage channels perms!!!')
        return

    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = prefix

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f)

    ctx.send(f'the prefix has been successfully changed to {prefix}')


@client.command(aliases=['8Ball', 'EightBall', 'eightBall', '8ball', '8b', '8B'])
async def eightball(ctx, *, question):
    responses = ["It is certain.",
                 "It is decidedly so.",
                 "Without a doubt.",
                 "Yes - definitely.",
                 "You may rely on it.",
                 "As I see it, yes.",
                 "Most likely.",
                 "Outlook good.",
                 "Yes.",
                 "Signs point to yes.",
                 "Reply hazy, try again.",
                 "IDK.",
                 "Better not tell you now.",
                 "Cannot predict now.",
                 "Concentrate and ask again.",
                 "Don't count on it.",
                 "My reply is no.",
                 "My sources say no.",
                 "Outlook not so good.",
                 "Very doubtful."]
    await ctx.send(f':8ball: Question {question}.\n:8ball: Answer: {random.choice(responses)}.')


@client.command(aliases=['Kick', 'k', 'K'])
async def kick(ctx, member: discord.Member, *, reason=None):
    if not ctx.author.guild_permissions.manage_members:
        ctx.send(f'Oh, no! @{ctx.author}, we do not have manage members permission')
        return
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} has been kicked \nReason: {reason}.')


@client.command(aliases=['Ban', 'B', 'b'])
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned \nReason: {reason}.')


@client.command(aliases=['countm', 'cm', 'countmes', 'comes', 'countmsg'])
async def message_count(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    count = 0
    async for _ in channel.history(limit=None):
        count += 1
    await ctx.send("There were {} messages in {}.".format(count, channel.mention))


@client.command(name='purge')
async def purge(ctx, amount=11):
    if not ctx.author.guild_permissions.manage_messages:
        ctx.send(f'Wait whaaaaaaat? @{ctx.author} doesn\'t have manage messages permissions???')
        ctx.send(f'@{ctx.send} needs manage messages permissions to execute command "purge')
        return
    channel: discord.TextChannel = None
    channel = channel or ctx.channel
    user = ctx.author
    amount = amount + 1
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'@{user} Cleared {amount - 1} messages in #{channel} .')


@client.command()
async def on_message(message):
    if not message.author.guild_permissions.manage_messages:
        message.send(f'Wait whaaaaaaat? @{message.author} doesn\'t have manage messages permissions???')
        message.send(f'@{message.send} needs manage messages permissions to execute command "purge')
        return

    if message.author == client.user:
        return

    if message.content.startswith('purge a'):
        channel: discord.TextChannel = None
        channel = channel or message.channel
        count = 0
        async for _ in channel.history(limit=None):
            count += 1
        await message.channel.purge(limit=count + 1)
        await message.channel.send(f'Successfully cleared {count} messages of channel {channel.mention}.')


client.run('OTMyMTMzOTM2NjUyNDg0NjI4.YeOjYA.VYPUwOyUQYrOFo0VPjfKABrMIfI')
