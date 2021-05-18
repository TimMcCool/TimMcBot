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
from replit import db
import requests

import os
import scratchapi

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
    try:
        color = ctx.guild.get_member(client.user.id).color
        if str(color) == "#000000":
            color = discord.Color.teal()
    except Exception:
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


async def prefix_info(ctx, message):
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
    await message.reply(embed=embed)
    return

# init bot
client = commands.Bot(
    command_prefix=get_prefix,
    intents=discord.Intents.all(),
    allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False),
)
slash = SlashCommand(client, sync_commands=True)
client.owner_id = 807320710807552030
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
    loading="<a:loading:830584070706429963>"
)
assets = dict(
    tmc_server_animated="https://cdn.discordapp.com/attachments/818455648903626752/820791308032671764/ezgif-6-0fe2bac545b1.gif",
    info="https://cdn.discordapp.com/attachments/818455648903626752/822926559022809108/costume5_1.png",
)
categories = dict(
    leveling="🏆 Leveling",
    invitetracking="📨 Invite Tracking",
    minigames="🎲 Minigames",
    fun="😂 Fun",
    other="📁 Other",
    giveaways="🎉 Giveaways",
    polls="🗳️ Polls",
    utility="🛠️ Utility"
)

# load all extensions

for filename in os.listdir("./extensions"):
    if filename.endswith(".py"):
        client.load_extension(f"extensions.{filename[:-3]}")

# help command

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
                create_choice(name="Utility", value="utility"),
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
    embed = None
    cogs = list(client.cogs)

    if not category is None:
        if category in cogs:
            embed = await help_cog(ctx, category, prefix)
        elif category == "other":
            embed = await help_cog(ctx, None, prefix)
    if not embed is None:
        await ctx.send(embed=embed)
        embed = None
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
                + f"** :small_blue_diamond: "
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

    embed = discord.Embed(description="", color=get_client_color(ctx))
    embed.set_author(name=name, icon_url=client.user.avatar_url)
    embed.set_footer(text="<Required arguments> | (Optional arguments)")

    for command in client.commands:
        if command.cog is None:
            this_cog_name = None
        else:
            this_cog_name = command.cog.qualified_name
        params = ""
        if this_cog_name == cog_name and not command.hidden:
            for item in list(command.clean_params):
                if str(command.clean_params[item].default) == "<class 'inspect._empty'>":
                    if str(command.clean_params[item].kind) == "VAR_POSITIONAL":
                        params = f"{params} ({item})"
                    else:
                        params = f"{params} <{item}>"
                else:
                    params = f"{params} ({item})"

            commandinfo = ""
            if not command.brief is None:
                commandinfo += "➣ "+ command.brief 
            try:
                subcommands = None
                for subcmd in command.commands:
                    subcmd_params = ""

                    for item in subcmd.clean_params:
                        
                        if str(subcmd.clean_params[item].default) == "<class 'inspect._empty'>":
                            if str(subcmd.clean_params[item].kind) == "VAR_POSITIONAL":
                                subcmd_params = f"{subcmd_params} ({item})"
                            else:
                                subcmd_params = f"{subcmd_params} <{item}>"
                        else:
                            subcmd_params = f"{subcmd_params} ({item})"

                    if subcommands == None:
                        subcommands = "`" + prefix + subcmd.qualified_name + subcmd_params + "`"
                    else:
                        subcommands = (
                            subcommands + ", `" + prefix + subcmd.qualified_name + subcmd_params + "`"
                        )
                commandinfo += "\n➣ Subcommands: " + subcommands
            except Exception:
                pass
            embed.description += f"\n**{prefix + command.qualified_name + params}**\n"
            if not commandinfo == "":
                embed.description += commandinfo+"\n"
    embed.description += (
        f"\n*Enter `{prefix}help <command>` to get info on a certain command*"
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

            if str(command.clean_params[item].default) == "<class 'inspect._empty'>":
                if str(command.clean_params[item].kind) == "VAR_POSITIONAL":
                    params = f"{params} ({item})"
                else:
                    params = f"{params} <{item}>"
            else:
                params = f"{params} ({item})"

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

        subcommands = None
        try:
            for subcmd in command.commands:
                subcmd_params = ""
                for item in subcmd.clean_params:

                    if str(subcmd.clean_params[item].default) == "<class 'inspect._empty'>":
                        if str(subcmd.clean_params[item].kind) == "VAR_POSITIONAL":
                            subcmd_params = f"{subcmd_params} ({item})"
                        else:
                            subcmd_params = f"{subcmd_params} <{item}>"
                    else:
                        subcmd_params = f"{subcmd_params} ({item})"

                if subcommands == None:
                    subcommands = prefix + subcmd.qualified_name + subcmd_params
                else:
                    subcommands = (
                        subcommands + "\n" + prefix + subcmd.qualified_name + subcmd_params
                    )
            content +=  "**Subcommands:**\n```" + subcommands + "```\n"
        except Exception:
            pass

        content += "**Category:** " + cog
        embed.description = content
        return embed


# setup-process and prefixes (unfinished)

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
        await prefix_info(ctx, ctx.message)

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


# commands

@client.command(hidden=True)
#@commands.is_owner()
async def spy(ctx, *, guild: discord.Guild):
    embed = discord.Embed(title="Channels", color=get_client_color(ctx))
    embed.set_author(name=guild.name, icon_url=guild.icon_url)
    for channel in guild.channels:
        embed.add_field(name=channel.name, value="** **")
    embed.set_footer(text=str(guild.id))
    await ctx.send(embed=embed)




'''
@slash.subcommand(
    guild_ids=[806272849458495489],
    base="scratch",
    name="login",
    options=[
        dict(
            name="username",
            description="The username of your Scratch account",
            type=3,
            required="true"
        ),
        dict(
            name="password",
            description="The password of your Scratch account",
            type=3,
            required="true"
        )
    ]
)
async def scratch_login(ctx, username, password):
    try:
        await ctx.defer(hidden=True)
    except Exception:
        pass

    try:
        scratch = scratchapi.ScratchUserSession(username, password, remember_password=False)
    except Exception:
        await ctx.send(f"Couldn't log in to **{username}** ⚠ Please make sure you entered the correct username / password.", hidden=True)
    else:
        if scratch.tools.verify_session() is True:
            await ctx.send(f"Successfully logged in as **{username}** ✅", hidden=True)
        else:
            await ctx.send(f"The account **{username}** is banned! {emojis['ban']}", hidden=True)
'''
#news
@slash.slash(
    name="scratch",
    description="Displays information from scratch.mit.edu",
    options=[
        dict(
            name="page",
            description="What page do you want to see?",
            type=3,
            required="true",
            choices=[
                create_choice(
                    name="Scratch News",
                    value="0"
                ),
                create_choice(
                    name="Featured Projects",
                    value="1"
                ),
                create_choice(
                    name="Top loved",
                    value="2"
                ),
                create_choice(
                    name="Cloud game activity",
                    value="3"
                ),
                create_choice(
                    name="Curated projects",
                    value="4"
                ),
                create_choice(
                    name="Profile",
                    value="5"
                ),
                create_choice(
                    name="Message count",
                    value="6"
                )
            ]
        ),
    dict(
        name="scratcher",
        description="This is required for 'Profile' and 'Message count'",
        type=3,
        required="false"
        )
    ]
)
async def _scratch(ctx, page, scratcher=None):
    await ctx.defer()
    if int(page) == 0:
        await scratch_news(ctx)
    elif int(page) == 1:
        await featured(ctx)
    elif int(page) == 2:
        await top_loved(ctx)
    elif int(page) == 3:
        await cloudgames(ctx)
    elif int(page) == 4:
        await curated(ctx)
    elif int(page) == 5:
        await profile(ctx, scratcher)
    elif int(page) == 6:
        await messages(ctx, scratcher)

@client.group(aliases=["s"], brief="Displays info from scratch.mit.edu", description="Displays information from the Scratch website (scratch.mit.edu) on your server!")
async def scratch(ctx):
    if ctx.invoked_subcommand is None:
        await scratch_news(ctx)

@scratch.command(brief="Tells whether a project is marked as nfe / unsafe")
async def nfe(ctx, project):
    await scratch_nfe(ctx, project)

def get_project_id(proj):
    project_id = ""
    for i in proj:
        if i.isnumeric():
            project_id += i
    return int(project_id)

@scratch.command(aliases=["t"], brief="Shows you the thumbnail of a Scratch project")
async def thumbnail(ctx, project):
    project_id = get_project_id(project)
    embed = discord.Embed(title="Thumbnail", color=get_client_color(ctx))
    embed.set_author(name="👩‍💻 Scratch Projects", url="https://scratch.mit.edu/")
    embed.set_footer(text="Data taken from cdn2.scratch.mit.edu")
    embed.set_image(url=f"https://cdn2.scratch.mit.edu/get_image/project/{project_id}_480x360.png")
    await ctx.message.reply(embed=embed)

async def scratch_nfe(ctx, proj):
    project_id = get_project_id(proj)
    message = await ctx.message.reply("Checking ...")
    try:
        nfe = requests.get(f"https://jeffalo.net/api/nfe/?project={project_id}")
        nfe = json.loads(nfe.text)
        if nfe["status"] == "safe":
            await message.edit(content="🟢 This project is safe!")
        elif nfe["status"] == "notsafe":
            await message.edit(content="🔴 This project was marked as unsafe (NFE).")
        else:
            await message.edit(content="🟡 This project was not reviewed yet.")
    except Exception:
        await message.edit(content="An error occurred! 😼 Please try again! You should make sure this project exists.")

async def scratch_news(ctx):
    news = requests.get(f"https://api.scratch.mit.edu/news/")
    news = json.loads(news.text)
    embed = discord.Embed(title="Recent site updates", color=get_client_color(ctx))

    for item in news[0:5]:
        embed.add_field(name=item['headline'], value=f"{item['copy']}\n[More ...]({item['url']})")

    embed.set_thumbnail(url="https://www.logolynx.com/images/logolynx/0b/0bdbd10ab2fa7096299f7c78e1ac55f5.png")
    embed.set_author(name="📢 Scratch News", url="https://scratch.mit.edu/")
    embed.set_footer(text="Data taken from the Scratch API")

    await ctx.send(embed=embed)

#cloudgames
def get_cloud_game(proj_ids, name, embed, *, author="griffpatch"):
    values = []
    for proj_id in proj_ids:
        cloud = requests.get(f"https://clouddata.scratch.mit.edu/logs?projectid={proj_id}&limit=100&offset=0")
        cloud = json.loads(cloud.text)
        players = []
        for item in cloud:
            if int(item['timestamp']) < round((time.time() - 10) * 1000):
                break
            if not item['user'] in players:
                players.append(item['user'])
        if not players == []:
            values.append("```➤ "+"\n➤ ".join(players)+"```")
        else:
            values.append("```Noone playing```")
    value = ""
    i = 0
    for item in values:
        i += 1
        value = f"{value}**[Server {i}:](https://scratch.mit.edu/projects/{proj_ids[i-1]})**\n{item}{emojis['spacer']}\n"
    #embed.add_field(name=name, value=f"by [{author}](https://scratch.mit.edu/users/{author}) • [To project](https://scratch.mit.edu/projects/{proj_id})\n"+value, inline=True)
    embed.add_field(name=name, value=value)
    return embed

@scratch.command(aliases=["cg"], brief="Shows active players on popular cloud games")
@commands.cooldown(1, 60, commands.BucketType.user)
async def cloudgames(ctx):
    await cloudgames(ctx)

async def cloudgames(ctx):
    embed = discord.Embed(title="Loading ...", color=get_client_color(ctx))
    embed.set_author(name="☁️ Scratch cloud projects", icon_url="https://www.logolynx.com/images/logolynx/0b/0bdbd10ab2fa7096299f7c78e1ac55f5.png")
    message = await ctx.send(embed=embed)
    await message.add_reaction(emojis['loading'])

    embed.set_footer(text="Data taken from the Scratch cloud data logs")
    embed.title="Popular cloud games"

    embed = get_cloud_game([108566337], "slither.io Scratch", embed)
    embed = get_cloud_game([12785898, 378507713], "Cloud Platformer Multiplayer Fun", embed)
    embed = get_cloud_game([478790208, 478797222], "Taco Burp | Cloud", embed)
    embed = get_cloud_game([409593079, 409596803, 409686453], "Othello Online", embed, author="TimMcCool")
    embed = get_cloud_game([466980603], "Appel Multiplayer", embed, author="XShrunk")
    embed = get_cloud_game([443370138], "Pico's world (MMO)", embed, author="TimMcCool")

    await message.remove_reaction(emojis['loading'], client.user)
    await message.edit(embed=embed)

#featured
@scratch.command(aliases=["f"], brief="Shows recently featured projects")
@commands.cooldown(2, 3, commands.BucketType.user)
async def featured(ctx):
    await featured(ctx)

async def featured(ctx):
    featured = requests.get(f"https://api.scratch.mit.edu/proxy/featured")
    featured = json.loads(featured.text)["community_featured_projects"]
    embed = discord.Embed(title="Recently featured", color=get_client_color(ctx))

    for item in featured[0:9]:
        embed.add_field(name=item['title'][0:20], value=f"Creator: [@{item['creator']}](https://scratch.mit.edu/users/{item['creator']})\nLoves: {item['love_count']}\n[View project](https://scratch.mit.edu/projects/{item['id']})")

    embed.set_author(name="🐱 Scratch Projects", url="https://scratch.mit.edu/")
    embed.set_footer(text="Data taken from the Scratch API")
    embed.set_thumbnail(url="https://www.logolynx.com/images/logolynx/0b/0bdbd10ab2fa7096299f7c78e1ac55f5.png")

    await ctx.send(embed=embed)

#top loved
@scratch.command(aliases=["toploved", "tl"], brief="Shows projects that are currently top loved")
@commands.cooldown(2, 3, commands.BucketType.user)
async def top_loved(ctx):
    await top_loved(ctx)

async def top_loved(ctx):
    tl = requests.get(f"https://api.scratch.mit.edu/proxy/featured")
    tl = json.loads(tl.text)["community_most_loved_projects"]
    embed = discord.Embed(title="Top loved", color=get_client_color(ctx))

    for item in tl[0:20]:
        embed.add_field(name=item['title'][0:20], value=f"Creator: [@{item['creator']}](https://scratch.mit.edu/users/{item['creator']})\nLoves: {item['love_count']}\n[View project](https://scratch.mit.edu/projects/{item['id']})")

    embed.set_author(name="❤️ Scratch Projects", url="https://scratch.mit.edu/")
    embed.set_footer(text="Data taken from the Scratch API")
    embed.set_thumbnail(url="https://www.logolynx.com/images/logolynx/0b/0bdbd10ab2fa7096299f7c78e1ac55f5.png")

    await ctx.send(embed=embed)

#top remixed
@scratch.command(brief="Displays projects that are currently being curated", aliases=["c"])
@commands.cooldown(2, 3, commands.BucketType.user)
async def curated(ctx):
    await curated(ctx)

async def curated(ctx):
    c = requests.get(f"https://api.scratch.mit.edu/proxy/featured")
    c = json.loads(c.text)["curator_top_projects"]
    embed = discord.Embed(title="Curated", description=f"The current front page curator is [@{c[0]['curator_name']}](https://scratch.mit.edu/users/{c[0]['curator_name']})! Today, they are curating the following projects:", color=get_client_color(ctx))

    for item in c[0:5]:
        embed.add_field(name=item['title'][0:20], value=f"Creator: [@{item['creator']}](https://scratch.mit.edu/users/{item['creator']})\nLoves: {item['love_count']}\n[View project](https://scratch.mit.edu/projects/{item['id']})")

    embed.set_author(name="📁 Scratch Projects", url="https://scratch.mit.edu/")
    embed.set_footer(text="Data taken from the Scratch API")
    embed.set_thumbnail(url="https://www.logolynx.com/images/logolynx/0b/0bdbd10ab2fa7096299f7c78e1ac55f5.png")

    await ctx.send(embed=embed)

#profiles
@scratch.command(aliases=["p"], brief="Shows a Scratch profile")
@commands.cooldown(2, 3, commands.BucketType.user)
async def profile(ctx, *, scratcher):
    await profile(ctx, scratcher)

async def profile(ctx, scratcher):
    try:
        data = requests.get(f"https://api.scratch.mit.edu/users/{scratcher}")
        data = json.loads(data.text)
        embed = discord.Embed(title="Profile", color=get_client_color(ctx))

        embed.add_field(name="Country:", value=data['profile']['country'], inline=True)
        embed.add_field(name="Joined at:", value=data['history']['joined'], inline=True)
        if not data['profile']['bio'] == "":
            embed.add_field(name="About me:", value="```"+data['profile']['bio']+"```", inline=False)
        if not data['profile']['status'] == "":
            embed.add_field(name="What I am working on:", value="```"+data['profile']['status']+"```", inline=False)

        embed.set_thumbnail(url=data['profile']['images']['90x90'])
        embed.set_author(name="😸 "+data['username'], url=f"https://scratch.mit.edu/users/{data['username']}")
        embed.set_footer(text="Data taken from the Scratch API")

        await ctx.send(embed=embed)
    except Exception:
        await ctx.send(
            "The Scratch server is scratching its head! 😼 This user doesn't exist."
        )

#messages
@scratch.command(aliases=["unread", "m"], brief="Shows a Scratcher's unread messages count")
@commands.cooldown(2, 4, commands.BucketType.user)
async def messages(ctx, *, scratcher):
    await messages(ctx, scratcher)

async def messages(ctx, scratcher):
    try:
        count = requests.get(f"https://api.scratch.mit.edu/users/{scratcher}/messages/count")
        count = json.loads(count.text)['count']
        await ctx.send(f"**{scratcher}** has **{count}** unread messages! :postbox:")
    except Exception:
        await ctx.send(
            "The Scratch server is scratching its head! 😼 This user doesn't exist."
        )

#-------------

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


@slash.slash(name="invite", description="Add TimMcBot to your server!")
async def _invite(ctx):
    invite = discord.Embed(
        description="**[Invite link](https://discord.com/api/oauth2/authorize?client_id=800377812699447306&permissions=4294967287&scope=bot%20applications.commands)**",
        color=get_client_color(ctx),
    )
    invite.set_author(name="➕ Add me to your server!", icon_url=client.user.avatar_url)
    await ctx.send(embed=invite)
    
@client.command(
    brief="Add me to your server!",
    description="Run the command to add me to your server!",
)
async def invite(ctx):
    invite = discord.Embed(
        description="**[Invite link](https://discord.com/api/oauth2/authorize?client_id=800377812699447306&permissions=4294967287&scope=bot%20applications.commands)**",
        color=get_client_color(ctx),
    )
    invite.set_author(name="➕ Add me to your server!", icon_url=client.user.avatar_url)
    await ctx.send(embed=invite)

@client.command(
    brief="Vote for me on top.gg!"
)
async def vote(ctx):
    invite = discord.Embed(
        description="**[Vote on top.gg](https://top.gg/bot/800377812699447306/vote)**",
        color=get_client_color(ctx),
    )
    invite.set_author(name="🗳️ Want to support TimMcBot?", icon_url=client.user.avatar_url)
    await ctx.send(embed=invite)

@client.command()
async def status(ctx):
    invite = discord.Embed(
        description="**[Status page](https://stats.uptimerobot.com/GzPzwhJ5KD)**",
        color=get_client_color(ctx),
    )
    invite.set_author(name="📈 TimMcBot status", icon_url=client.user.avatar_url)
    await ctx.send(embed=invite)

@client.command(aliases=["log"], hidden=True)
@commands.is_owner()
async def logs(ctx):
    await ctx.send("https://timmcbot.tim135790.repl.co/__logs")

@client.command(aliases=["developer"], hidden=True)
@commands.is_owner()
async def dev(ctx):
    await ctx.send("https://replit.com/@Tim135790/TimMcBot")

# errors:

async def error_handler(ctx, error, prefix, *, slash=False):
    ErrMessage = discord.Embed(color=discord.Color.red())
    ErrContent = None
    if isinstance(error, commands.CommandNotFound) and slash is False:
        if ctx.prefix == "<@!800377812699447306> ":
            await prefix_info(ctx, ctx.message)
        return
            
    elif isinstance(error, commands.MissingRequiredArgument) and slash is False:
        if ctx.command.qualified_name == "clap":
            await ctx.send("You forgot to enter the text I'm supposed to clap! :clap:")
            return
        elif ctx.command.qualified_name == "reverse":
            await ctx.send("Please also enter a text so I can esrever it!")
            return
        elif ctx.command.qualified_name == "8ball":
            await ctx.send("You didn't ask anything. :thinking:")
            return
        elif ctx.command.qualified_name == "emojify":
            await ctx.send(
                "Please also enter a text so I can :regional_indicator_e: :regional_indicator_m: :regional_indicator_o: :regional_indicator_j: :regional_indicator_i: :regional_indicator_f: :regional_indicator_y: it!"
            )
            return            
        elif ctx.command.qualified_name == "spoiler":
            await ctx.send(
                "Please also enter a text so I can write it with ||S||||p||||o||||i||||l||||e||||r||||s||!"
            )
            return
        else:
            params = ""
            command=ctx.command
            for item in command.clean_params:
                if str(command.clean_params[item].default) == "<class 'inspect._empty'>":
                    if str(command.clean_params[item].kind) == "VAR_POSITIONAL":
                        params = f"{params} ({item})"
                    else:
                        params = f"{params} <{item}>"
                else:
                    params = f"{params} ({item})"
            ErrMessage.title = "Command incomplete"
            ErrContent = f":bulb: **How to use this command:** `{prefix}{ctx.command.qualified_name}{params}`\n\n**`<{error.param.name}>`** is a required arguments that is missing."
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("This member was not found! 👀")
        return
    elif isinstance(error, commands.UserNotFound):
        await ctx.send("This user was not found! 👀")
        return
    elif isinstance(error, commands.RoleNotFound):
        await ctx.send("This role was not found! 👀")
        return
    elif isinstance(error, commands.MissingPermissions):
        ErrMessage.title = "Permission problem"
        ErrContent = f"You need the **`{'`** and the **`'.join(error.missing_perms)}`** permission to run this command!"
    elif isinstance(error, commands.BotMissingPermissions):
        ErrMessage.title = "Missing access"
        ErrContent = f"I need the **`{'`** and the **`'.join(error.missing_perms)}`** permission to execute this command!"
    elif isinstance(error, commands.NotOwner):
        ErrMessage.title = "Permission problem"
        ErrContent = "Only the bot developer is authorized to use this command."
    elif isinstance(error, commands.CheckFailure):
        ErrMessage.title = "Check failure"
        ErrContent = f"You are missing some requirements to run this command."
    elif isinstance(error, commands.DisabledCommand):
        ErrMessage.title = "Command disabled"
        ErrContent = "This command has been disabled by the bot developer."
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.message.reply(
            f"Command on cooldown! You can use it again in **{ceil(error.retry_after*10)/10} seconds**. ⏳"
        )
        return
    elif isinstance(error, commands.BadArgument) or isinstance(
        error, commands.ArgumentParsingError
    ):
        ErrMessage.title = "Invalid arguments"
        params = ""
        for item in ctx.command.clean_params:
            params = f"{params} <{item}>"
        ErrContent = f":bulb: **How to use this command:** `{prefix}{ctx.command.qualified_name}{params}`"
    elif isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, discord.Forbidden):
            ErrMessage.title = error.original.text
            ErrContent = f"I don't have the permissions that I need to run your command."
        else:
            ErrMessage.title = "Error"
            ErrContent = "Something went wrong!"
    else:
        ErrMessage.title = "Error"
        ErrContent = "Something went wrong!"
    ErrMessage.description = ErrContent
    try:
        await ctx.send(embed=ErrMessage)
    except Exception:
        try:
            await ctx.send("Something went wrong! :frowning:", hidden=True)
        except Exception:
            pass
    if not slash is True:
        try:
            if ErrMessage.title == "Permission problem":
                await ctx.message.add_reaction("🚫")
            else:
                await ctx.message.add_reaction("⚠️")
        except Exception:
            return

@client.event
async def on_command_error(ctx, error):
    prefix = get_prefix(client, ctx.message)[1]
    await error_handler(ctx, error, prefix)

@client.event
async def on_slash_command_error(ctx, error):
    if isinstance(error, discord_slash.error.CheckFailure):
        await ctx.send("This slash command doesn't work in Direct Messages! ⚠", hidden=True)
    else:
        await error_handler(ctx, error, "+", slash=True)

# events:


@client.event
async def on_message(message):

    # CHECK IF MESSAGE AUTHOR IS BANNED

    with open("json_files/bans.json", "r") as b:
        bans = json.load(b)

    if message.guild is not None and message.author.bot is False:
        if message.guild.id == 751545225498984609:

            if message.author.id == 710033069226328095:
                if "@everyone" or "@here" in message.content:
                    await message.channel.send("<@!710033069226328095> Krasser ping! 😱 Die anderen Mitglieder werden ***begeistert*** sein :angry:")
        
            if "718811967342772285" in message.content:
                await message.channel.send(message.author.mention+" Ey, hör auf meinen Chef zu pingen! :angry:")

            if str(message.guild.owner.id) in message.content:
                await message.channel.send(message.author.mention+" Ey, hör auf den Server-Boss zu pingen! :angry:")


    # IF NOT BANNED

    if not str(message.author.id) in bans and not message.content == "":
        if not message.author.bot:
            if str(message.channel.type) == "private":

                # LOG DM

                embed = discord.Embed(
                    title="Direct Message to TimMcBot",
                    description=message.content,
                    color=discord.Colour.gold(),
                )
                embed.set_author(
                    name=str(message.author), icon_url=message.author.avatar_url
                )
                embed.set_footer(text=f"User {message.author.id}")
                Webhook("https://discord.com/api/webhooks/833734042193100870/v7DHtWZw-5YY4odYXKZudzPLIBlpVNJDlxp4LEPAlFBHGg1GOCp9-WAhKPF4LkoP6n-l").send(embed=embed)
            
            else:

                if message.content == "<@!800377812699447306>":

                    # SEND PREFIX INFO
                    await prefix_info(message.channel, message)
                
                await client.process_commands(message)


@client.event
async def on_ready():
    print(f"\n{client.user.name} is now online!\n")
    
    server_count = len(client.guilds)
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"+help | {server_count} servers")
    )
    

    with open("json_files/2048highscores.json", "w") as d:
        json.dump(dict(db["2048highscores"]), d, indent=4)

    with open("json_files/globalchat.json", "w") as d:
        json.dump(dict(db["globalchat"]), d, indent=4)
    
    prefixes = dict(db["prefixes"])
    for key in list(prefixes.keys()):
        prefixes[key] = list(prefixes[key])

    with open("json_files/prefixes.json", "w") as d:
        json.dump(prefixes, d, indent=4)

    leveling = dict(db["leveling"])
    for key in list(leveling.keys()):
        leveling[key] = dict(leveling[key])
        for sub_key in list(leveling[key].keys()):
            leveling[key][sub_key] = dict(leveling[key][sub_key])
            leveling[key][sub_key]["daily"] = dict(leveling[key][sub_key]["daily"])
            leveling[key][sub_key]["weekly"] = dict(leveling[key][sub_key]["weekly"])

    with open("json_files/leveling.json", "w") as d:
        json.dump(leveling, d, indent=4)

    levelroles = dict(db["levelroles"])
    for key in list(levelroles.keys()):
        levelroles[key] = dict(levelroles[key])

    with open("json_files/levelroles.json", "w") as d:
        json.dump(levelroles, d, indent=4)

    polls = dict(db["polls"])
    for key in list(polls.keys()):
        polls[key] = dict(polls[key])
        for sub_key in list(polls[key].keys()):
            polls[key][sub_key] = dict(polls[key][sub_key])
            polls[key][sub_key]["options"] = list(polls[key][sub_key]["options"])

    with open("json_files/levelroles.json", "w") as d:
        json.dump(levelroles, d, indent=4)
    
    rr = dict(db["rr"])
    for key in list(rr.keys()):
        rr[key] = dict(rr[key])
        for sub_key in list(rr[key].keys()):
            rr[key][sub_key] = dict(rr[key][sub_key])

    with open("json_files/rr.json", "w") as d:
        json.dump(rr, d, indent=4)

    save_data_on_db.start()
    

    '''
    guild = await client.fetch_guild(800008691289292821)
    async for entry in guild.audit_logs(limit=100):
        print('{0.user} did {0.action} to {0.target}'.format(entry))
    '''
    '''
    channels = await guild.fetch_channels()
    for channel in channels:
        print(channel.name, "\n", channel.id, "\n\n")
        if channel.id == 802712321608515614:
            print(channel)
            #webhook = await channel.create_webhook(name="-Tim-")
            #print(webhook.url)
    chilly_dragon_webhook = "https://discord.com/api/webhooks/828997712086827098/uG9Hvnfpgee6Wp_SvUYJIGr8DdKRNVdj8M51H8Oz98hMbyv0RKbNIUF2bc38M2HCMRzs"
    test_webhook = "https://discord.com/api/webhooks/828741183622479912/-rz0PNJN-K8PON40q_peXQlRaqG8lkwxMCK_Idh__UhPiMvdfCh9PhRDW6hh2E7hqhAd"
    
    embed=discord.Embed(
        title=":warning: WARNING :warning:",
        description="You just got **PINGED!**",
        color=discord.Color.teal()
    )
    embed.set_image(url="https://cdn.discordapp.com/avatars/718811967342772285/f14f4f3916b31537f947f06d7038cce0.webp?size=1024")
    embed.set_footer(text="Did I scare you? O_O")
    #await webhook.send("<@!479742278932496384>", embed=embed, username="-Tim-", avatar_url=str(client.user.avatar_url))
    #Webhook(test_webhook).send("<@!479742278932496384>", embed=embed, username="-Tim-", avatar_url=str(client.user.avatar_url))

    channel = await client.fetch_channel(814076464571875358)
    print(channel)
    for message in (await channel.history().flatten()):
        print(f"[{message.author}]\n[{message.content}]\n\n")'''''''''''''''

@client.event
async def on_command(ctx):
    print(
        f"[{ctx.author}]: {ctx.message.content}\nGUILD: {ctx.guild.name}\nCHANNEL: {ctx.channel.name}\n"
    )

@client.event
async def on_guild_join(guild):
    server_count = len(client.guilds)
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"+help | {server_count} servers")
    )

@client.event
async def on_guild_remove(guild):
    server_count = len(client.guilds)
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"+help | {server_count} servers")
    )


@client.event
async def on_slash_command(ctx):
    try:
        print(
            f"[{ctx.author}]:\nSLASH_NAME: {ctx.name}\nGUILD: {ctx.guild.name}\nCHANNEl: {ctx.channel.name}\n"
        )
    except AttributeError:
        print(
            f"[{ctx.author}]:\nSLASH_NAME: {ctx.name}\nGUILD: DM\nCHANNEl: DMChannel\n"
        )

# tasks

@tasks.loop(seconds=20)
async def save_data_on_db():
    with open("json_files/2048highscores.json", "r") as d:
        db["2048highscores"] = dict(json.load(d))
    with open("json_files/globalchat.json", "r") as d:
        db["globalchat"] = dict(json.load(d))
    with open("json_files/prefixes.json", "r") as d:
        db["prefixes"] = dict(json.load(d))
    with open("json_files/leveling.json", "r") as d:
        db["leveling"] = dict(json.load(d))
    with open("json_files/levelroles.json", "r") as d:
        db["levelroles"] = dict(json.load(d))
    with open("json_files/polls.json", "r") as d:
        db["polls"] = dict(json.load(d))
    with open("json_files/rr.json", "r") as d:
        db["rr"] = dict(json.load(d))

# bot

keep_alive.keep_alive()
client.run(os.getenv("TOKEN"))
