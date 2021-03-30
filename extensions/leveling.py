import discord
import random
from random import randint
from discord.ext import commands, tasks
from discord.ext.commands import CheckFailure
import json
from datetime import datetime, timedelta
from os import system, name as OSname
from main import assets, emojis, get_prefix, is_not_private, get_client_color
import asyncio
import math
import time
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

# variables


def is_guild_owner(ctx):
    return ctx.author.id == ctx.guild.owner_id


class leveling(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        prefixes = get_prefix(self.client, message)

        if str(message.channel.type) == "private":
            return
        if message.author.bot:
            return
        if message.content == "":
            return
        # LEVELING

        # LOAD JSON

        with open("json_files/leveling.json", "r") as d:
            servers = json.load(d)
        # ADD DATA THAT ISN'T IN DICT YET

        new = False
        if not str(message.guild.id) in servers:
            servers[str(message.guild.id)] = {}
        if not str(message.author.id) in servers[str(message.guild.id)]:
            servers[str(message.guild.id)][str(message.author.id)] = {
                "messages": 0,
                "xp": 0,
                "last": 0,
                "name": str(message.author),
                "daily": {"xp": 0, "day": 0},
                "weekly": {"xp": 0, "week": 0},
            }
            new = True
        # CREATE VARS
        old_users = servers[str(message.guild.id)]
        data = servers[str(message.guild.id)][str(message.author.id)]

        # GET OLD RANK

        keys = list(old_users.keys())
        tbefore = []
        i = 0
        for item in keys:
            i += 1
            tbefore.append([old_users[item], item])
            if item == str(message.author.id):
                tbefore_index = i

        def check(elem):
            return elem[0]["xp"]

        t = sorted(tbefore, key=check, reverse=True)
        old_t = [t]

        # UPDATE DATA

        data["messages"] = data["messages"] + 1
        data["name"] = str(message.author)
        change_xp = (round(time.time())) - data[
            "last"
        ] > 60 and not message.content.startswith(tuple(prefixes))
        if change_xp:
            old_level = getlevel(data["xp"])[0]
            new_xp = randint(14, 20)
            data["xp"] = data["xp"] + new_xp
            new_level = getlevel(data["xp"])[0]
            if old_level != new_level:
                await message.channel.send(
                    f"GG {message.author.mention}, you just advanced to **Level {new_level}**! Keep it up! :partying_face:"
                )
            data["last"] = round(time.time())
            if (
                data["daily"]["day"]
                == (datetime.today() - datetime.utcfromtimestamp(0)).days
            ):
                data["daily"] = {
                    "xp": data["daily"]["xp"] + new_xp,
                    "day": (datetime.today() - datetime.utcfromtimestamp(0)).days,
                }
            else:
                data["daily"] = {
                    "xp": new_xp,
                    "day": (datetime.today() - datetime.utcfromtimestamp(0)).days,
                }
            if data["weekly"]["week"] == math.floor(
                ((datetime.today() - datetime.utcfromtimestamp(0)).days - 4) / 7
            ):
                data["weekly"] = {
                    "xp": data["weekly"]["xp"] + new_xp,
                    "week": math.floor(
                        ((datetime.today() - datetime.utcfromtimestamp(0)).days - 4) / 7
                    ),
                }
            else:
                data["weekly"] = {
                    "xp": new_xp,
                    "week": math.floor(
                        ((datetime.today() - datetime.utcfromtimestamp(0)).days - 4) / 7
                    ),
                }
        # SAVE UPDATED DATA IN JSON

        servers[str(message.guild.id)][str(message.author.id)] = data
        with open("json_files/leveling.json", "w") as d:
            json.dump(servers, d, indent=4)
        # UPDATE RANK ROLES

        if change_xp:
            old_rank = getmyrank(str(message.author.id), old_t[0])
            if new is True:
                old_rank += 5
            # GET NEW RANK

            tbefore[tbefore_index - 1] = [data, str(message.author.id)]
            t = sorted(tbefore, key=check, reverse=True)

            new_rank = getmyrank(str(message.author.id), t)

            # CHECK IF RANK ROLES UPDATE

            if new_rank != old_rank:
                with open("json_files/levelroles.json", "r") as r:
                    levelroles = json.load(r)
                if str(message.guild.id) in levelroles:
                    guild_lr = levelroles[str(message.guild.id)]
                    if str(new_rank) in guild_lr:

                        for index in guild_lr:
                            try:
                                role = message.guild.get_role(guild_lr[str(index)])
                            except Exception:
                                continue
                            try:
                                for member in role.members:
                                    try:
                                        await member.remove_roles(role)
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                            try:
                                member = message.guild.get_member(
                                    int(t[int(index) - 1][1])
                                )
                                try:
                                    await member.add_roles(role)
                                except Exception:
                                    pass
                            except Exception:
                                pass

    @cog_ext.cog_slash(
        name="rank",
        description="Shows a user's rank card",
        options=[
            dict(
                name="user",
                description="Do you want to see the rank card of a specific user?",
                type=5,
                required="false",
            )
        ],
    )
    async def _rank(self, ctx, user=None):
        if user is None:
            await rankcard(ctx, ctx.author, True)
        elif user.bot:
            await ctx.send("This user is a bot and can't get ranked! :robot:")
        else:
            await rankcard(ctx, user, False)

    @commands.command(
        brief="Shows the rank card of a user", aliases=["r", "ranking", "rang"]
    )
    async def rank(self, ctx, *, user: discord.Member):
        if user.bot:
            await ctx.send("This user is a bot and can't get ranked! :robot:")
        else:
            await rankcard(ctx, user, False)

    @commands.Cog.listener()
    @rank.error
    async def rank_me(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await rankcard(ctx, ctx.message.author, True)

    @cog_ext.cog_slash(
        name="leaderboard",
        description="Shows the server's leaderboard",
        options=[
            dict(
                name="type",
                description="What leaderboard do you want to see?",
                type=3,
                required="true",
                choices=[
                    create_choice(name="normal", value="0"),
                    create_choice(name="weekly", value="1"),
                    create_choice(name="daily", value="2"),
                    create_choice(name="web", value="3"),
                ],
            )
        ],
    )
    async def _levels(self, ctx, type):
        mode = int(type)
        if mode == 3:
            await ctx.send(
                f"Here is **{ctx.guild.name}**'s web leaderboard:\nhttps://timmcbot.tim135790.repl.co/leaderboard/?guild={ctx.guild.id}"
            )
        else:
            await levellist(self, ctx, mode=mode)

    @commands.group(
        brief="Shows the server's leaderboard",
        aliases=["leaderboard", "lb", "leaders", "ranklist", "rangliste"],
    )
    async def levels(self, ctx):
        if ctx.invoked_subcommand is None:
            await levellist(self, ctx, mode=0)

    @levels.command(brief="Shows the server's weekly leaderboard", aliases=["w"])
    async def weekly(self, ctx):
        await levellist(self, ctx, mode=1)

    @levels.command(brief="Shows the server's daily leaderboard", aliases=["d"])
    async def daily(self, ctx):
        await levellist(self, ctx, mode=2)

    @levels.command(brief="Provides the link to the web leaderboard")
    async def web(self, ctx):
        await ctx.send(
            f"Here is **{ctx.guild.name}**'s web leaderboard:\nhttps://timmcbot.tim135790.repl.co/leaderboard/?guild={ctx.guild.id}"
        )

    @commands.group(
        brief="Shows the rank role settings",
        aliases=["rankrole", "levelroles", "lbroles"],
    )
    async def rankroles(self, ctx):
        if ctx.invoked_subcommand is None:
            with open("json_files/levelroles.json", "r") as d:
                levelroles = json.load(d)
            embed = discord.Embed(
                title="Rank roles",
                description=f"will be automatically given to members with a specific TimMcBot rank\n{emojis['spacer']}",
                color=get_client_color(ctx),
            )
            if str(ctx.guild.id) in levelroles:
                keys = list(levelroles[str(ctx.guild.id)].keys())
                for i in range(len(keys)):
                    keys[i] = int(keys[i])
                keys = sorted(keys)
                for key in keys:
                    data = levelroles[str(ctx.guild.id)]
                    embed.description += f"\n**➲ Rank #{key}**\n{emojis['spacer']}<@&{data[str(key)]}>\n{emojis['spacer']}"
                    # embed.add_field(name="Rank #"+str(key), value=f"<@&{data[str(key)]}>", inline=True)
            else:
                embed.add_field(name="No rank roles set on this server!", value="** **")
            embed.add_field(
                name="How to set a rank role:",
                value="```+rankroles set <rank> <role>```",
                inline=False,
            )
            embed.add_field(
                name="How to remove the rank role of a rank:",
                value="```+rankroles remove <rank>```",
                inline=False,
            )
            embed.set_footer(
                text="You need the 'Manage Server' permission to set rank roles."
            )
            embed.set_author(
                name=f"🎭 {ctx.message.guild.name}", icon_url=ctx.message.guild.icon_url
            )
            await ctx.send(embed=embed)

    @rankroles.command(brief="Sets a rank role")
    @commands.has_permissions(manage_guild=True)
    async def set(self, ctx, rank: int, *, role: discord.Role):
        # try:
        origin_role = role
        origin_rank = rank
        if role.managed is True:
            await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="This role can't be used because it is managed by a bot or by an intergration.",
                    color=discord.Color.red(),
                )
            )
            await ctx.message.add_reaction("⚠")
        else:
            with open("json_files/levelroles.json", "r") as d:
                levelroles = json.load(d)
            if not str(ctx.guild.id) in levelroles:
                levelroles[str(ctx.guild.id)] = {}
            levelroles[str(ctx.guild.id)][str(rank)] = role.id
            with open("json_files/levelroles.json", "w") as d:
                json.dump(levelroles, d, indent=4)
            with open("json_files/leveling.json", "r") as d:
                users = json.load(d)[str(ctx.message.guild.id)]
            with open("json_files/leveling.json", "r") as d:
                users = json.load(d)[str(ctx.guild.id)]
            keys = list(users.keys())
            tbefore = []
            for item in keys:
                tbefore.append([users[item], item])

            def check(elem):
                return elem[0]["xp"]

            t = sorted(tbefore, key=check, reverse=True)

            roles = []
            guild_lr = levelroles[str(ctx.guild.id)]
            for index in guild_lr:
                try:
                    role = ctx.message.guild.get_role(guild_lr[str(index)])
                    roles.append(role)
                except Exception:
                    continue
                for member in role.members:
                    try:
                        await member.remove_roles(role)
                    except Exception:
                        pass
            for rank in guild_lr:
                try:
                    role = ctx.message.guild.get_role(guild_lr[str(rank)])
                    if not int(rank) > len(t):
                        member = ctx.message.guild.get_member(int(t[int(rank) - 1][1]))
                        await member.add_roles(role)
                except Exception:
                    pass
            # except Exception:
            """  await ctx.send(embed=discord.Embed(title="Error", description=f"**I can't manage that role because it is above my highest roles!** To fix that problem, go to the role settings of this server and drag the TimMcBot role above {role.mention}!", color=discord.Color.red()))
        await ctx.message.add_reaction("⚠")
      else:"""
            await ctx.send(
                f"**Success!** The role {origin_role.mention} will be automatically assigned to the member with rank **{origin_rank}.**"
            )
            await ctx.message.add_reaction(emojis["checkmark"])

    @rankroles.command(brief="Removes the rank role for a rank")
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx, rank: int):
        with open("json_files/levelroles.json", "r") as d:
            levelroles = json.load(d)
        if str(ctx.guild.id) in levelroles:
            if str(rank) in levelroles[str(ctx.guild.id)]:
                levelroles[str(ctx.guild.id)].pop(str(rank))
                await ctx.send(
                    f"**Success!** The rank role for rank **{rank}** has been removed."
                )
                await ctx.message.add_reaction(emojis["checkmark"])
                if levelroles[str(ctx.guild.id)] == {}:
                    levelroles.pop(str(ctx.guild.id))
                with open("json_files/levelroles.json", "w") as d:
                    json.dump(levelroles, d, indent=4)


async def levellist(self, ctx, *, mode):
    with open("json_files/leveling.json", "r") as d:
        servers = json.load(d)
    if not str(ctx.guild.id) in servers:
        await ctx.send("No messages have been sent since TimMcBot was added!")
        return
    symbol = ":small_blue_diamond:"
    keys = list(servers[str(ctx.guild.id)].keys())
    tbefore = []
    for item in keys:
        tbefore.append([servers[str(ctx.guild.id)][item], item])
    if mode == 0:

        def check(elem):
            return elem[0]["xp"]

        t = sorted(tbefore, key=check, reverse=True)
    elif mode == 1:

        def check(elem):
            try:
                return elem[0]["weekly"]["xp"]
            except IndexError:
                return 0

        t = sorted(tbefore, key=check, reverse=True)

        def check(elem):
            try:
                return elem[0]["weekly"]["week"] == math.floor(
                    ((datetime.today() - datetime.utcfromtimestamp(0)).days - 4) / 7
                )
            except Exception:
                return False

        t = list(filter(check, t))
        if len(t) == 0:
            await ctx.send("Noone has gained XP yet this week!")
            return
    elif mode == 2:

        def check(elem):
            try:
                return elem[0]["daily"]["xp"]
            except IndexError:
                return 0

        t = sorted(tbefore, key=check, reverse=True)

        def check(elem):
            try:
                return (
                    elem[0]["daily"]["day"]
                    == (datetime.today() - datetime.utcfromtimestamp(0)).days
                )
            except Exception:
                return False

        t = list(filter(check, t))
        if len(t) == 0:
            await ctx.send("Noone has gained XP yet today!")
            return
    prefix = get_prefix(self.client, ctx.message)
    if len(t) < 6:
        board = await levelcard(self, ctx, t, None, 0, symbol, mode)
        await ctx.send(None, embed=board)
    else:
        seiten = math.ceil(len(t) / 5)
        seite = 1
        tcropped = t[0:5]
        board = await levelcard(
            self, ctx, tcropped, f"📖 Page {seite} of {seiten}", 0, symbol, mode
        )
        if random.randint(0, 5) == 0 and mode == 0:
            message = await ctx.send(
                f"**Tip:** Enter `{prefix[1]}levels weekly` to see the weekly leaderboard. :bulb:",
                embed=board,
            )
        elif random.randint(0, 5) == 1 and mode == 0:
            message = await ctx.send(
                f"**Tip:** Enter `{prefix[1]}levels daily` to see the daily leaderboard. :bulb:",
                embed=board,
            )
        else:
            message = await ctx.send(embed=board)
        await message.add_reaction("⏮"), await message.add_reaction(
            "◀"
        ), await message.add_reaction("▶"), await message.add_reaction("⏭")
        while True:

            def check(reaction, user):
                return (
                    reaction.message == message
                    and str(reaction.emoji) in ["⏮", "◀", "▶", "⏭"]
                    and user == ctx.author
                )

            try:
                reaction, user = await self.client.wait_for(
                    "reaction_add", timeout=None, check=check
                )
            except asyncio.TimeoutError:
                return
            else:
                if str(reaction.emoji) == "▶" and not seite == seiten:
                    seite += 1
                elif str(reaction.emoji) == "◀" and not seite == 1:
                    seite -= 1
                elif str(reaction.emoji) == "⏮":
                    seite = 1
                elif str(reaction.emoji) == "⏭":
                    seite = seiten
                tcropped = t[seite * 5 - 5 : seite * 5]
                board = await levelcard(
                    self,
                    ctx,
                    tcropped,
                    f"📖 Page {seite} of {seiten}",
                    (seite - 1) * 5,
                    symbol,
                    mode,
                )
                await message.edit(embed=board)
                await reaction.remove(user)


async def levelcard(self, ctx, tcropped, footer, low_rank, symbol, mode):
    if mode == 0:
        content = "The most active server members:\n\n"
    elif mode == 1:
        content = "This week's most active server members:\n\n"
    elif mode == 2:
        content = "Today's most active server members:\n\n"
    i = 0
    for item in tcropped:
        i += 1
        if mode == 0:
            level = getlevel(item[0]["xp"])
            userinfo = f" {symbol} **{item[0]['name']}**\n{emojis['spacer']}Level `{level[0]}`\n{emojis['spacer']}{emojis['coin']} `{item[0]['xp']}/{level[1]+1}`\n\n"
        elif mode == 1:
            userinfo = f" {symbol} **{item[0]['name']}**\n{emojis['spacer']}{emojis['coin']} `{item[0]['weekly']['xp']}`\n\n"
        elif mode == 2:
            userinfo = f" {symbol} **{item[0]['name']}**\n{emojis['spacer']}{emojis['coin']} `{item[0]['daily']['xp']}`\n\n"
        if i + low_rank == 1:
            content = f"{content}**:first_place:**{userinfo}"
        elif i + low_rank == 2:
            content = f"{content}**:second_place:**{userinfo}"
        elif i + low_rank == 3:
            content = f"{content}**:third_place:**{userinfo}"
        else:
            content = f"{content}**#{i+low_rank}**{userinfo}"
    if mode == 0:
        content = (
            content
            + f":small_orange_diamond: [Click here](https://timmcbot.tim135790.repl.co/leaderboard/?guild={ctx.guild.id}) to visit the **web leaderbaord.**"
        )
    elif mode == 1:
        today = now = datetime.today()
        today = datetime(today.year, today.month, today.day)
        next_reset = datetime.today() + timedelta(
            days=(timedelta(days=7 - now.weekday()) + today - now).days + 1
        )
        content = (
            content
            + f":small_orange_diamond: **Next reset:** Monday ({next_reset.strftime('%m/%d/%Y')}) at 12am UTC"
        )
    elif mode == 2:
        content = (
            content + ":small_orange_diamond: **Next reset:** Tomorrow at 12am UTC"
        )
    board = discord.Embed(
        title=ctx.guild.name, description=content, color=get_client_color(ctx)
    )
    if not footer is None:
        board.set_footer(text=footer)
    board.set_thumbnail(url=ctx.guild.icon_url)
    if mode == 0:
        board.set_author(name="🏆 Leaderboard")
    elif mode == 1:
        board.set_author(name="📅 Weekly leaderboard")
    elif mode == 2:
        board.set_author(name="📆 Daily leaderboard")
    return board


async def rankcard(ctx, user, myself):
    with open("json_files/leveling.json", "r") as d:
        servers = json.load(d)
    if str(ctx.guild.id) in servers:
        users = servers[str(ctx.guild.id)]
        if str(user.id) in users:
            keys = list(users.keys())
            tbefore = []
            umessages = users[str(user.id)]
            for item in keys:
                tbefore.append([users[item], item])

            def check(elem):
                return elem[0]["xp"]

            t = sorted(tbefore, key=check, reverse=True)

            level, levelup = getlevel(umessages["xp"])
            rank = getmyrank(str(user.id), t)
            t = None
            content = f"**Level: {level}**{emojis['spacer']}"
            content = (
                f"{content}**Messages: {umessages['messages']}**{emojis['spacer']}"
            )
            content = f"{content}**{umessages['xp']}** / {levelup+1} {emojis['coin']} {emojis['spacer']}"
            if rank == 1:
                content = f"{content}:first_place: **Rank: #{rank}**"
            elif rank == 2:
                content = f"{content}:second_place: **Rank: #{rank}**"
            elif rank == 3:
                content = f"{content}:third_place: **Rank: #{rank}**"
            else:
                content = f"{content}:trophy: **Rank: #{rank}**"
            card = discord.Embed(
                title="Rank Card", description=content, color=discord.Colour.random()
            )
            card.set_author(name="👤 " + str(user), icon_url=str(user.avatar_url))
            card.set_footer(
                text=f"Server: {ctx.guild.name}", icon_url=str(ctx.guild.icon_url)
            )
            random_number = random.randint(0, 4)
            if random_number == 0:
                await ctx.send(
                    "**Tip:** To prevent spamming, you can only gain XP once every minute. :bulb:",
                    embed=card,
                )
            elif random_number == 1:
                await ctx.send(
                    "**Tip:** You don't get XP for TimMcBot commands! :bulb:",
                    embed=card,
                )
            else:
                await ctx.send(embed=card)
        else:
            if myself is True:
                await ctx.send(
                    "You aren't ranked yet! Send some messages first, then try again."
                )
            else:
                await ctx.send("This user isn't ranked yet!")
    else:
        if myself is True:
            await ctx.send(
                "You aren't ranked yet! Send some messages first, then try again."
            )
        else:
            await ctx.send("This user isn't ranked yet!")


def getlevel(XP):
    level, i = 2, -1
    while i < XP:
        level, i = level + 1, i + level * 50
    return level - 3, i


def getmyrank(auth, t):
    rank = 0
    u = (t[0])[1]
    while not u == auth:
        rank += 1
        u = (t[rank])[1]
    rank += 1
    return rank


def setup(client):
    client.add_cog(leveling(client))