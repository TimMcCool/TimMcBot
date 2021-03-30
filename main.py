# imports and installs
import discord
from discord.ext import commands, tasks
from discord.ext.commands import MissingPermissions, CheckFailure
import time, datetime
import random
from random import randint
import flask
from flask import Flask
import keep_alive
from itertools import cycle
import json
from dhooks import Webhook
import math
from math import ceil
import inspect
import os
import subprocess


def install(name):
    subprocess.call(["pip", "install", name])


try:
    import discord_slash
except ModuleNotFoundError:
    install("discord-py-slash-command")
    import discord_slash
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

# functions
def is_not_private(ctx):
    return not ctx.guild_id is None


def get_client_color(ctx):
    color = ctx.guild.get_member(client.user.id).color
    if str(color) == "#000000":
        color = discord.Color.teal()
    return color


def get_prefix(client, message):
    with open("json_files/prefixes.json", "r") as d:
        serverdata = json.load(d)
    try:
        if str(message.guild.id) in serverdata:
            prefixes = serverdata[str(message.guild.id)]
            prefixes.insert(0, "<@!800377812699447306> ")
            return prefixes
        else:
            return ["<@!800377812699447306> ", "+"]
    except AttributeError:
        if str(message) in serverdata:
            prefixes = serverdata[str(message)]
            prefixes.insert(0, "<@!800377812699447306> ")
            return prefixes
        else:
            return ["<@!800377812699447306> ", "+"]


# init
client = commands.Bot(
    command_prefix=get_prefix,
    intents=discord.Intents.all(),
    allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False),
)
slash = SlashCommand(client, sync_commands=True)
status = "+help"
client.author_id = 718811967342772285
client.remove_command("help")

with open("json_files/bans.json", "r") as b:
    bans = json.load(b)
emojis = dict(
    spacer="<:spacer:815004931878158376>",
    blobchain="<a:blobchain_1:808675562159341568>",
    ban="<:ban_1:808677659805483079>",
    # checkmark = "<a:checkmark_1:808767689375612959>",
    checkmark="👌",
    coin="XP",
    diamond=":diamond_shape_with_a_dot_inside:",
    bluespacer="<:bluespacer:818086140649144330>",
    f_in_the_chat="<:f_in_the_chat:822516052151107644>",
    tmb_icon="<:TimMcBot:822934684803268648>",
    info="<:info:823643485813866518>",
)
assets = dict(
    tmc_server_animated="https://cdn.discordapp.com/attachments/818455648903626752/820791308032671764/ezgif-6-0fe2bac545b1.gif",
    info="https://cdn.discordapp.com/attachments/818455648903626752/822926559022809108/costume5_1.png",
)
categories = dict(
    leveling="🏆 Leveling",
    minigames="🎲 Minigames",
    fun="😂 Fun",
    other="📁 Other",
    giveaways="🎉 Giveaways",
    polls="🗳 Polls",
)

# load all extensions
for filename in os.listdir("./extensions"):
    if filename.endswith(".py"):
        client.load_extension(f"extensions.{filename[:-3]}")
# help:
@slash.slash(
    name="help",
    description="Don't know what to do? This shows you the help message.",
    options=[
        dict(
            name="category",
            description="If you want to get info on a certain category, select it now!",
            type=3,
            required="false",
            choices=[
                create_choice(name="Leveling", value="leveling"),
                create_choice(name="Minigames", value="minigames"),
                create_choice(name="Giveaways", value="giveaways"),
                create_choice(name="Fun", value="fun"),
                create_choice(name="Polls", value="polls"),
                create_choice(name="Other", value="other"),
            ],
        ),
        dict(
            name="command",
            description="If you want to get info on a certain command, specify it now!",
            type=3,
            required="false",
        ),
    ],
)
@commands.check(is_not_private)
async def _help(ctx, category=None, command=None):
    prefixes = get_prefix(client, ctx.guild_id)
    prefix = prefixes[1]

    cogs = list(client.cogs)

    if not category is None:
        if category in cogs:
            embed = await help_cog(ctx, category, prefix)
        elif category == "other":
            embed = await help_cog(ctx, None, prefix)
    if not command is None:
        embed = await help_command(ctx, command, prefix)
    if category is None and command is None:
        embed = await help_home(ctx, prefix)
    if not embed is None:
        await ctx.send(embed=embed)


@client.command(brief="Shows this message")
async def help(ctx, *, command=""):
    if ctx.prefix == "<@!800377812699447306> ":
        prefixes = get_prefix(client, ctx.message)
        prefix = prefixes[1]
    else:
        prefix = ctx.prefix
    cogs = list(client.cogs)

    if command == "":
        embed = await help_home(ctx, prefix)
    elif command in cogs:
        embed = await help_cog(ctx, command, prefix)
    elif command == "other":
        embed = await help_cog(ctx, None, prefix)
    else:
        embed = await help_command(ctx, command, prefix)
    if not embed is None:
        await ctx.send(embed=embed)


async def help_home(ctx, prefix):
    cogs = list(client.cogs)
    cogs.append("other")
    embed = discord.Embed(
        description=f"Enter `{prefix}help <command>` to get info on a certain command",
        color=get_client_color(ctx),
    )
    embed.set_author(name="Help", icon_url=client.user.avatar_url)
    for item in cogs:
        if item in categories:
            embed.description = (
                embed.description
                + "\n\n**"
                + categories[item]
                + "** 🔹 "
                + f"`{prefix}help {item}`"
            )
    embed.description += f"\n\n:small_orange_diamond: There are **slash commands** too! Type / to see them."
    return embed


async def help_cog(ctx, cog_name, prefix):
    if cog_name in categories:
        name = categories[cog_name]
    elif cog_name is None:
        name = "📁 Other"
    else:
        name = cog_name

    embed = discord.Embed(title=name, description="", color=get_client_color(ctx))

    for command in client.commands:
        if command.cog is None:
            this_cog_name = None
        else:
            this_cog_name = command.cog.qualified_name
        params = ""
        if this_cog_name == cog_name and not command.hidden:
            for item in list(command.clean_params):
                params = f"{params} <{item}>"
            # embed.description += prefix+command.qualified_name+params+"\n"
            commandinfo = ""
            if not command.brief is None:
                commandinfo += command.brief + "\n"
            try:
                subcommands = None
                for subcmd in command.commands:
                    subcmd_params = ""

                    for item in subcmd.clean_params:
                        subcmd_params = f"{subcmd_params} <{item}>"
                    if subcommands == None:
                        subcommands = "\n" + prefix + subcmd.qualified_name + subcmd_params
                    else:
                        subcommands = (
                            subcommands + "\n" + prefix + subcmd.qualified_name + subcmd_params
                        )
                commandinfo += "``````𝗦𝘂𝗯𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀:" + subcommands
            except Exception:
                pass
            if commandinfo == "":
                embed.add_field(
                    name=prefix + command.qualified_name + params,
                    value="** **",
                    inline=False,
                )
            else:
                embed.add_field(
                    name=prefix + command.qualified_name + params,
                    value="```"+commandinfo+"```",
                    inline=False,
                )
    embed.description += (
        f"Enter `{prefix}help <command>` to get info on a certain command"
    )
    return embed


async def help_command(ctx, command, prefix):
    command_wio_prefix = command.replace(prefix, "")
    command = client.get_command(command_wio_prefix)
    if command is None or command.hidden:
        await ctx.send(f"No command named **`{command_wio_prefix}`** found.")
        return None
    else:
        params, alts = "", None
        for item in command.clean_params:
            params = f"{params} <{item}>"
        for alt in command.aliases:
            if command.full_parent_name == "":
                if alts == None:
                    alts = f"{prefix}{alt}{params}"
                else:
                    alts = f"{alts}, {prefix}{alt}{params}"
            else:
                if alts == None:
                    alts = f"{prefix}{command.full_parent_name} {alt}{params}"
                else:
                    alts = f"{alts}, {prefix}{command.full_parent_name} {alt}{params}"
        embed = discord.Embed(
            title=f"`{prefix}{command.qualified_name}{params}`",
            color=get_client_color(ctx),
        )
        content = ""
        if not alts is None:
            content += "**Alternate:**\n```" + alts + "```\n"
        if command.description == "":
            if not command.brief is None:
                content += "**Description:\n**" + command.brief + "\n\n"
        else:
            content += "**Description:**\n" + command.description + "\n\n"
        if not command.usage is None:
            content = (content + command.usage).format(prefix) + "\n"
        if not command.help is None:
            content += ":bulb: **Tip:**\n" + command.help + "\n\n"
        if command.cog_name is None:
            cog = "📁 Other"
        else:
            cog = categories[command.cog_name]
        if not command.full_parent_name == "":
            content += (
                f"**Subcommand of:**\n```{prefix}" + command.full_parent_name + "```\n"
            )
        try:
            subcommands = None
            for subcmd in command.commands:
                params = ""
                for item in subcmd.clean_params:
                    params = f"{params} <{item}>"
                if subcommands == None:
                    subcommands = prefix + subcmd.qualified_name + params
                else:
                    subcommands = (
                        subcommands + "\n" + prefix + subcmd.qualified_name + params
                    )
            content += "**Subcommands:**\n```" + subcommands + "```\n"
        except Exception:
            pass
        content += "**Category:** " + cog
        embed.description = content
        return embed


# setup-process


@client.command(hidden=True, aliases=["reloadcogs"])
@commands.is_owner()
async def reload(ctx):
    for filename in os.listdir("./extensions"):
        if filename.endswith(".py"):
            client.reload_extension(f"extensions.{filename[:-3]}")
    await ctx.message.delete()


@client.command(enabled=False, hidden=True)
@commands.has_permissions(manage_guild=True)
async def setup(ctx):
    color = ctx.guild.get_member(client.user.id).top_role.color
    embed = discord.Embed(
        title="Step 1",
        description=f"**{ctx.author.name}, please answer the following questions!** You have 5 minutes for each question.",
        color=get_client_color(ctx),
    )
    embed.set_author(name="⚙️ Setup process", icon_url=client.user.avatar_url)
    await ctx.send(embed=embed)


@client.group(brief="Shows the bot's prefixes", aliases=["prefixes"])
async def prefix(ctx):
    if ctx.invoked_subcommand is None:
        with open("json_files/prefixes.json", "r") as d:
            serversettings = json.load(d)
        if str(ctx.guild.id) in serversettings:
            prefixes = serversettings[str(ctx.guild.id)]
            prefixes.insert(0, "<@!800377812699447306> ")
        else:
            prefixes = ["<@!800377812699447306>", "+"]
        description = ""
        i = 0
        for prefix in prefixes:
            i += 1
            description += f"{i}. {prefix}\n"
        embed = discord.Embed(
            title=f"{len(prefixes)} Prefixes",
            description=description,
            color=get_client_color(ctx),
        )
        embed.set_author(name="⚙️ " + ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f"{prefixes[1]}prefix add <prefix> | {prefixes[1]}prefix remove <prefix>")
        await ctx.send(embed=embed)


@prefix.command(brief="Admins can add a prefix with this command")
@commands.has_permissions(manage_guild=True)
async def add(ctx, *, prefix):
    if prefix.startswith("/"):
        await ctx.send(
            "TimMcBot prefixes can't start with / - that prefix is reserved to slash commands!"
        )
    elif len(prefix) > 15:
        await ctx.send("TimMcBot prefixes can't be longer than **15 letters!**")
    else:
        with open("json_files/prefixes.json", "r") as d:
            serversettings = json.load(d)
        if str(ctx.guild.id) in serversettings:
            prefixes = serversettings[str(ctx.guild.id)]
        else:
            prefixes = ["+"]
        if prefix == "<@!800377812699447306> " or prefix in prefixes:
            await ctx.send(f"{prefix} is already a prefix!")
        elif len(prefixes) > 13:
            await ctx.send("This server **reached the limit** of TimMcBot prefixes! (15) 🚫")
        else:
            prefixes.append(prefix)
            serversettings[str(ctx.guild.id)] = prefixes
            with open("json_files/prefixes.json", "w") as d:
                json.dump(serversettings, d, indent=4)
            await ctx.send(f"The prefix {prefix} has been sucessfully added! 👌")


@prefix.command(brief="Admins can remove a prefix with this command")
@commands.has_permissions(manage_guild=True)
async def remove(ctx, *, prefix):
    if prefix == "<@!800377812699447306> ":
        await ctx.send(f"The prefix {prefix} can't be removed!")
    else:
        with open("json_files/prefixes.json", "r") as d:
            serversettings = json.load(d)
        if str(ctx.guild.id) in serversettings:
            prefixes = serversettings[str(ctx.guild.id)]
        else:
            prefixes = ["+"]
        if prefix in prefixes:
            if len(prefixes) == 1:
                await ctx.send(
                    f"There must be **at least one** prefix beside {client.user.mention}! Please add another prefix before removing this one."
                )
            else:
                prefixes.remove(prefix)
                serversettings[str(ctx.guild.id)] = prefixes
                with open("json_files/prefixes.json", "w") as d:
                    json.dump(serversettings, d, indent=4)
                await ctx.send(f"The prefix {prefix} has been removed.")
        else:
            await ctx.send("That's not a TimMcBot prefix!")


# slash-commands:
@slash.slash(
    guild_ids=[806272849458495489],
    name="invites",
    description="Shows the invites a user created.",
    options=[
        dict(
            name="user",
            description="The user you want to get info on",
            type=6,
            required="false",
        )
    ],
)
async def _invites(ctx, user=None):
    if user is None:
        user = ctx.author
    embed = await get_invites(ctx, user)
    embed.set_author(name="📎 " + str(user), icon_url=user.avatar_url)
    await ctx.send(embed=embed)


# commands:
@client.command(brief="Shows bot latency")
async def ping(ctx):
    await ctx.send(
        f"{ctx.message.author.mention} It took me **{round(client.latency * 1000)}ms** to answer! :clock: That's pretty fast, isn't it?"
    )


@client.command(hidden=True, enabled=False, aliases=["poem"])
async def potionz(ctx):
    await ctx.send(
        embed=discord.Embed(
            title="Potionz",
            description="Potionz is lacking awesomeness.\nIt brings users helplessness.\nMy goodness, it brought me sadness!\nHow're you going to enhance this evil business?\n\n*This amazing poem was written by the Scratcher @icmy123 and modified by @TimMcCool*",
            color=discord.Color.green(),
        )
    )


@client.command()
async def invites(ctx, *, user: discord.User):
    embed = await get_invites(ctx, user)
    embed.set_author(name="📎 " + str(user), icon_url=user.avatar_url)
    await ctx.send(embed=embed)


@invites.error
async def test(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = await get_invites(ctx, ctx.author)
        embed.set_author(name="📎 " + str(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


async def get_invites(ctx, user):
    embed = discord.Embed(
        title="Invites",
        description="This member hasn't created any invites yet!",
        color=get_client_color(ctx),
    )
    guild_invites = await ctx.guild.invites()
    invited_users = 0
    for invite in guild_invites:
        if invite.inviter.id == user.id:
            embed.add_field(
                name="discord.gg/" + invite.id,
                value=f"Created at: {invite.created_at.strftime('%m/%d/%Y')}\nChannel: {invite.channel.mention}\nUses: {invite.uses}\n",
            )
            invited_users += invite.uses
            embed.description = ""
    embed.set_footer(text=f"Total invited users: {invited_users}")
    return embed


@client.command(
    brief="Sends user a DM",
    description="Sends a user a Direct Message (DM) 📬",
    help="If you have permission to make use of slash commands, you can also use `/dm`!",
)
async def dm(ctx, receiver: discord.User, *, message):
    await ctx.message.delete()
    success = await send_dm(ctx, receiver, message)
    if success is True:
        await ctx.send(
            ctx.author.mention,
            embed=discord.Embed(
                title="DM sent! 📬",
                description=f"Your DM was sucessfully sent to **{receiver}**",
                color=discord.Color.green(),
            ),
        )
    else:
        embed = discord.Embed(
            title="This user doesn't accept DMs from me. :frowning:",
            description="Therefore, I wasn't able to send your message.",
            color=discord.Color.red(),
        )
        await ctx.send(ctx.author.mention, embed=embed)


@slash.slash(
    name="dm",
    description="Sends a user a Direct Message (DM) 📬",
    options=[
        dict(
            name="receiver",
            description="Who do you want to send the DM to?",
            type=6,
            required="true",
        ),
        dict(
            name="message",
            description="Your message (Nothing inappropiate or mean please)",
            type=3,
            required="true",
        ),
    ],
)
@commands.check(is_not_private)
async def _dm(ctx, receiver: discord.User, message):
    success = await send_dm(ctx, receiver, message)
    if success is True:
        await ctx.send(f"DM sent to **{receiver}**", hidden=True)
    else:
        await ctx.send(
            f"Failed to send DM because **{receiver}** doesn't accept DMs from me",
            hidden=True,
        )
        await ctx.send(hidden=True, embed=embed)


async def send_dm(ctx, receiver: discord.User, message):
    try:
        to = receiver
        channel = await to.create_dm()

        embed = discord.Embed(
            title="Direct Message",
            description=message,
            color=discord.Color.random(),
            timestamp=datetime.datetime.now(),
        )
        embed.set_author(name=f"🖊 Author: {ctx.author}")
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_footer(text=f"Server: {ctx.guild.name}", icon_url=ctx.guild.icon_url)
        await channel.send(embed=embed)

        dmlog = client.get_channel(814442695976157214)
        await dmlog.send(f"the original was sent to *{to}*", embed=embed)
    except discord.Forbidden:
        return False
    else:
        return True


@dm.error
async def no_dm(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "Please mention the **user** you want to sent the DM and the **message** you want to send them. :pencil2:"
        )


@client.command(
    brief="Add me to your server!",
    description="Run the command to add me to your server!",
)
async def invite(ctx):
    invite = discord.Embed(
        description="**[Click here to add TimMcBot to your server.](https://discord.com/api/oauth2/authorize?client_id=800377812699447306&permissions=4294967287&scope=bot%20applications.commands)**",
        color=get_client_color(ctx),
    )
    invite.set_author(name="Invite me to your server!", icon_url=client.user.avatar_url)
    await ctx.send(embed=invite)


@slash.slash(name="invite", description="Add TimMcBot to your server!")
async def _invite(ctx):
    invite = discord.Embed(
        description="**[Click here to add TimMcBot to your server.](https://discord.com/api/oauth2/authorize?client_id=800377812699447306&permissions=4294967287&scope=bot%20applications.commands)**",
        color=discord.Color.teal(),
    )
    invite.set_author(name="Add me to your server!", icon_url=client.user.avatar_url)
    await ctx.send(embed=invite)


# errors:

''''''


@client.event
async def on_command_error(ctx, error):
    prefix = get_prefix(client, ctx.message)[1]
    ErrMessage = discord.Embed(color=discord.Color.red())
    ErrContent = None
    if isinstance(error, commands.CommandNotFound):
        return

    elif isinstance(error, commands.MissingRequiredArgument):
        if ctx.command.qualified_name in [
            "rank",
            "connect4",
            "tictactoe",
            "dm",
            "rickroll",
            "invites",
        ]:
            return
        else:
            params = ""
            for item in ctx.command.clean_params:
                params = f"{params} <{item}>"
            ErrMessage.title = "Command incomplete"
            ErrContent = f":bulb: How to use this command: `{prefix}{ctx.command.qualified_name}{params}`\n\n`<{error.param.name}>` is a required arguments that is missing."
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("This member was not found! 🔍")
        return
    elif isinstance(error, commands.UserNotFound):
        await ctx.send("This user was not found! 🔎")
        return
    elif isinstance(error, commands.MissingPermissions):
        ErrMessage.title = "Permission problem"
        ErrContent = f"You need the **`{' and the `'.join(error.missing_perms)}`** permission to run this command!"
    elif isinstance(error, commands.NotOwner):
        ErrMessage.title = "Permission problem"
        ErrContent = "Only the bot developer is authorized to use this command."
    elif isinstance(error, commands.CheckFailure):
        ErrMessage.title = "Check failure"
        ErrContent = f"You are missing some requirements to run this command.\n\n**About the command:**\n{ctx.command.description}"
    elif isinstance(error, commands.DisabledCommand):
        ErrMessage.title = "Command disabled"
        ErrContent = "This command has been disabled by the bot developer."
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"Command on cooldown! You can use it again in **{ceil(error.retry_after)} seconds**. ⏳"
        )
        return
    elif isinstance(error, commands.BadArgument) or isinstance(
        error, commands.ArgumentParsingError
    ):
        ErrMessage.title = "Invalid arguments"
        params = ""
        for item in ctx.command.clean_params:
            params = f"{params} <{item}>"
        ErrContent = f":bulb: How to use this command: `{prefix}{ctx.command.qualified_name}{params}`"
    elif isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, discord.Forbidden):
            ErrMessage.title = error.original.text
            ErrContent = f"I don't have the permissions that I need to run your command.\n\n:bulb: **Tip:**\nI'd recommend you to give me the **`Administrator`** permission, that will definitely fix this problem."
        else:
            await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="Something went wrong!",
                    color=discord.Colour.red(),
                )
            )
            await ctx.message.add_reaction("⚠️")
            return
    elif not ctx.command.qualified_name in ["dm"]:
        await ctx.send(
            embed=discord.Embed(
                title="Error",
                description="Something went wrong!",
                color=discord.Colour.red(),
            )
        )
        await ctx.message.add_reaction("⚠️")
        return
    ErrMessage.description = ErrContent
    await ctx.send(embed=ErrMessage)
    try:
        if ErrMessage.title == "Permission problem":
            await ctx.message.add_reaction("🚧")
        else:
            await ctx.message.add_reaction("⚠️")
    except Exception:
        return


@client.event
async def on_slash_command_error(ctx, ex):
    if isinstance(ex, discord_slash.error.CheckFailure):
        await ctx.defer()
        await ctx.send("This slash command doesn't work in Direct Messages! ⚠")


# events:


@client.event
async def on_message(message):

    # CHECK IF MESSAGE AUTHOR IS BANNED

    with open("json_files/bans.json", "r") as b:
        bans = json.load(b)
    # IF NOT BANNED

    if not str(message.author.id) in bans and not message.content == "":
        if not message.author.bot:
            if str(message.channel.type) == "private":

                # LOG DM

                throughlog = await client.fetch_channel(816102465573355531)
                nachricht = discord.Embed(
                    title="Direct Message to TimMcBot",
                    description=message.content,
                    color=discord.Colour.gold(),
                )
                nachricht.set_author(
                    name=str(message.author), icon_url=message.author.avatar_url
                )
                nachricht.set_footer(text=f"User {message.author.id}")
                await throughlog.send(embed=nachricht)
            else:
                await client.process_commands(message)


@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=status)
    )
    print(f"\n{client.user.name} is now online!\n")


@client.event
async def on_command(ctx):
    print(
        f"[{ctx.author}]: {ctx.message.content}\nGUILD = {ctx.guild.name}\nCHANNEl = {ctx.channel.name}\n"
    )


@client.event
async def on_slash_command(ctx):
    print(
        f"[{ctx.author}]:\nSLASH_NAME = {ctx.name}\nGUILD = {ctx.guild.name}\nCHANNEl = {ctx.channel.name}\n"
    )


# bot

keep_alive.keep_alive()
client.run(os.getenv("TOKEN"))
