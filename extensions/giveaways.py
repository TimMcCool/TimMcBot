import discord
import random
from random import randint
from discord.ext import commands, tasks
import json
from main import assets, emojis, get_prefix, is_not_private, get_client_color
import asyncio
from extensions import leveling
from datetime import datetime, timedelta
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from replit import db

#getting data from replit database
gaws = dict(db['giveaways'])
for key in list(gaws.keys()):
    gaws[key] = dict(gaws[key])
with open("json_files/giveaways.json", "w") as g:
    json.dump(gaws, g, indent=4)

questions = [
    "What's the prize for your giveaway?",
    "How long do you want your giveaway to last?",
    "How many winners do you want?",
    "What channel do you want the giveaway to be in?",
    "Is there a role users need?",
    "How many messages do members need?",
    "How many users do members need to have invited?",
    "Is there a server users need to be in?",
    "What TimMcBot level do members need?",
]

descriptions = [
    "",
    "Enter the duration like that:\n```glsl\n3 weeks = 3w\n1 day and 20 hours = 1d, 20h\n30 minutes and 10 seconds = 30m, 10s```",
    "Enter a number between 0 and 99.",
    "Name it, mention it or reply with its id.",
    "Name it, mention it or reply with its id.",
    "",
    "",
    "Name it, reply with its id or send an invite link to the server.",
    "",
]

footer = "'skip' if there is none | 'finish' to skip all upcoming questions"

contents = [
    "{}",
    "Neat! Your giveaway will be for **{}**!",
    "Cool! Your giveaway will last **{}**.",
    "Sweet! Your giveaway will have **{} winner(s)!**",
    "{}",
    "{}",
    "{}",
    "{}You almost made it!",
    "{}Last question!",
]


async def create_giveaway(self, ctx, data=None):
    keys = [
        "name",
        "endtime",
        "winners",
        "channel",
        "role",
        "messages",
        "invites",
        "guild",
        "level",
        "author",
    ]

    if data is None:
        data, q = {}, 0
        last_ans, error = "", False
        channel = ctx.channel

        while q < len(questions):
            if not error:
                if channel.id == 825784641289715762 and q == 4:
                    embed = discord.Embed(
                        title="Information",
                        description="You're creating your giveaway **in <#825784641289715762>!**\n*Therefore, the required role has been automatically set to **<@&802225483655413761>** and question 5 will be skipped.*",
                        color=discord.Color.magenta(),
                    )
                    embed.set_author(
                        name="💎 Your giveaway", icon_url=ctx.author.avatar_url
                    )
                    await ctx.send(embed=embed)
                    last_ans = ""
                    role = ctx.guild.get_role(802225483655413761)
                    data["role"] = role.id
                    q += 1
                    continue
                else:
                    embed = discord.Embed(
                        title=questions[q],
                        description=descriptions[q],
                        color=get_client_color(ctx),
                    )
                    embed.set_author(
                        name=f"🎁 Question {q+1}", icon_url=ctx.author.avatar_url
                    )
                    if q > 3:
                        embed.set_footer(text=footer)
                    if q == 5:
                        embed.add_field(
                            name="Note:",
                            value="Only messages that have been sent since TimMcBot was added count.",
                        )
                    if q == 7:
                        embed.add_field(
                            name="Note:",
                            value="You can only choose servers TimMcBot is in.",
                        )
                    await ctx.send(contents[q].format(last_ans), embed=embed)

            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author

            try:
                msg = await self.client.wait_for("message", timeout=300.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send(
                    None,
                    embed=discord.Embed(
                        title=":alarm_clock: Timeout", color=discord.Colour.red()
                    ),
                )
                return
            else:
                last_ans, error = "", False
                if msg.content.lower() == "skip" or msg.content.lower() == "none" or msg.content.lower() == "no":
                    if q > 3:
                        data[keys[q]] = None
                    else:
                        await ctx.send(
                            embed=discord.Embed(
                                description="You **can't skip** this question!",
                                color=discord.Colour.red(),
                            )
                        )
                        error = True
                        continue
                elif msg.content == "finish" and q > 3:
                    while q < len(questions):
                        data[keys[q]] = None
                        q += 1
                    continue
                elif msg.content == "cancel":
                    await ctx.send(
                        None,
                        embed=discord.Embed(
                            title="Process cancelled", color=discord.Colour.red()
                        ),
                    )
                    return
                else:
                    if q == 1:
                        try:
                            payload = msg.content
                            element, duration = "", timedelta()
                            for i in payload:
                                if i.isnumeric():
                                    element = f"{element}{i}"
                                elif not element == "":
                                    element = int(element)
                                    if i == "w":
                                        duration = duration + timedelta(weeks=element)
                                    elif i == "d":
                                        duration = duration + timedelta(days=element)
                                    elif i == "h":
                                        duration = duration + timedelta(hours=element)
                                    elif i == "m":
                                        duration = duration + timedelta(minutes=element)
                                    elif i == "s":
                                        duration = duration + timedelta(seconds=element)
                                    element = ""
                            if duration == timedelta():
                                await ctx.send(
                                    embed=discord.Embed(
                                        description="**You didn't enter a valid duration.** Please try again!",
                                        color=discord.Colour.red(),
                                    )
                                )
                                error = True
                                continue
                            else:
                                last_ans = duration
                                data[keys[q]] = (datetime.now() + duration).strftime(
                                    "%m/%d/%Y, %H:%M:%S"
                                )
                                q += 1
                                continue
                        except OverflowError:
                            await ctx.send(
                                embed=discord.Embed(
                                    title="Overflow Error",
                                    description="The values you entered for the duration of your giveaway are **too big.**\n\nPlease try again!",
                                    color=discord.Colour.red(),
                                )
                            )
                            error = True
                            continue
                        except Exception:
                            await ctx.send(
                                embed=discord.Embed(
                                    description="**Something went wrong.** Please try again!",
                                    color=discord.Colour.red(),
                                )
                            )
                            error = True
                            continue
                    elif q == 2:
                        try:
                            last_ans = int(msg.content)
                        except Exception:
                            await ctx.send(
                                embed=discord.Embed(
                                    description="**That's not a number.** Please try again!",
                                    color=discord.Colour.red(),
                                )
                            )
                            error = True
                            continue
                        else:
                            if not 0 <= last_ans < 100:
                                await ctx.send(
                                    embed=discord.Embed(
                                        description="A giveaway can only have **between 0 and 99 winners.** Please try again!",
                                        color=discord.Colour.red(),
                                    )
                                )
                                error = True
                                continue
                    elif q == 3:
                        for char in msg.content:
                            if char.isdigit():
                                last_ans = f"{last_ans}{char}"
                        if last_ans == "":
                            channel = None
                        else:
                            last_ans = int(last_ans)
                            channel = discord.utils.get(ctx.guild.channels, id=last_ans)
                        if channel is None:
                            channel = discord.utils.get(ctx.guild.channels, name=msg.content)
                            if channel is None:
                                await ctx.send(
                                    embed=discord.Embed(
                                        title="Couldn't fetch that channel",
                                        description="Please try again!\nMake sure to enter a **valid channel** that the bot **can access.**",
                                        color=discord.Colour.red(),
                                    )
                                )
                                error = True
                                continue
                            else:
                                last_ans = channel.id   
                        perms = channel.permissions_for(ctx.author)
                        if perms.send_messages is False or perms.view_channel is False:
                            await ctx.send(
                                embed=discord.Embed(
                                    title="Error",
                                    description="You are **not allowed to create giveaways in this channel** because you can't send messages there!\nPlease choose another channel.",
                                    color=discord.Colour.red(),
                                )
                            )
                            error = True
                            continue                                 
                    elif q == 4:
                        for char in msg.content:
                            if char.isdigit():
                                last_ans = f"{last_ans}{char}"
                        try:
                            last_ans = int(last_ans)
                            role = ctx.guild.get_role(last_ans)
                            role.id
                        except Exception:
                            role = discord.utils.get(ctx.guild.roles, name=msg.content)
                            if role is None:
                                await ctx.send(
                                    embed=discord.Embed(
                                        title="Couldn't get that role",
                                        description="Please try again!\nMake sure to **mention** a valid role **or send its id.**",
                                        color=discord.Colour.red(),
                                    )
                                )
                                error = True
                                continue
                            else:
                                last_ans = role.id
                    elif q == 5 or q == 6 or q == 8:
                        try:
                            last_ans = int(msg.content)
                        except Exception:
                            await ctx.send(
                                embed=discord.Embed(
                                    description="**That's not a number.** Please try again!",
                                    color=discord.Colour.red(),
                                )
                            )
                            error = True
                            continue
                    elif q == 7:
                        guild = discord.utils.get(self.client.guilds, name=msg.content)
                        if guild is None:
                            try:
                                try:
                                    guild_id = int(msg.content)
                                except Exception:
                                    invite = await self.client.fetch_invite(msg.content)
                                    guild = invite.guild
                                    if isinstance(guild, discord.PartialInviteGuild):
                                        embed = discord.Embed(
                                            description="You can only choose servers TimMcBot is in!\n\nPlease [add TimMcBot to the server](https://discord.com/api/oauth2/authorize?client_id=800377812699447306&permissions=4294967287&scope=bot%20applications.commands) or choose another one.",
                                            color=discord.Colour.red(),
                                        )
                                        embed.set_author(
                                            name=f"TimMcBot isn't in '{guild.name}'",
                                            icon_url=str(guild.icon_url),
                                        )
                                        await ctx.send(embed=embed)
                                        error = True
                                        continue
                                    last_ans = guild.id
                                else:
                                    guild = await self.client.fetch_guild(guild_id)
                                    last_ans = guild.id
                            except Exception:
                                
                                await ctx.send(
                                    embed=discord.Embed(
                                        description="**Couldn't fetch that server.** Please try again!",
                                        color=discord.Colour.red(),
                                    )
                                )
                                error = True
                                continue
                        else:
                            last_ans = guild.id
                    else:
                        last_ans = msg.content
                    data[keys[q]] = last_ans
                q += 1
                if q > 3:
                    last_ans = ""
    else:
        guild = data["guild"]
        if not guild is None:
            data["guild"] = data["guild"].id
        role = data["role"]
        if not role is None:
            data["role"] = data["role"].id
        channel = data["channel"]
        data["channel"] = data["channel"].id
        data["ended"] = False
    embed = discord.Embed(
        title=data["name"],
        color=discord.Colour.random(),
        timestamp=datetime.strptime(data["endtime"], "%m/%d/%Y, %H:%M:%S"),
    )
    embed.set_author(name="🎉 Giveaway", icon_url=ctx.author.avatar_url)
    embed.set_footer(text="Ends at")

    content = f"Hosted by {ctx.author.mention}\n❖ Winners: {data['winners']}"
    if not data["messages"] is None:
        content = content + f"\n❖ Required messages: {data['messages']}"
    if not data["level"] is None:
        content = content + f"\n❖ Required TimMcBot level: {data['level']}"
    if not data["invites"] is None:
        content = content + f"\n❖ Required invited users: {data['invites']}"

    if not data["role"] is None:
        content = content + f"\n\n**» Required role:**\n{role.mention}"
    if not data["guild"] is None:
        content = content + f"\n\n**» You have to be in:**\n{guild.name}"

    content = content + "\n\n**React with 🎉 to enter!**"
    embed.description = content

    data["author"] = ctx.author.id
    data["ended"] = False

    try:
        gaw = await channel.send(embed=embed)
        data["url"] = gaw.jump_url
        await gaw.add_reaction("🎉")
        with open("json_files/giveaways.json", "r") as g:
            gaws = json.load(g)
        gaws[str(gaw.id)] = data
        
        db['giveaways'] = gaws
        with open("json_files/giveaways.json", "w") as g:
            json.dump(gaws, g, indent=4)
    except discord.Forbidden:
        embed = discord.Embed(
            title="Error",
            description=f"Please make sure that I have permission to send messages in {channel.mention}.",
            color=discord.Colour.red(),
        )
    except Exception:
        embed = discord.Embed(
            title="Error", description="Could not create your giveaway.", color=discord.Colour.red()
        )
    else:
        embed = discord.Embed(
            title="Success!",
            description=f"Your giveaway has been created in {channel.mention}.",
            color=discord.Colour.green(),
        )
        embed.set_author(name="📝 Giveaway created", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)

# cogs


class giveaways(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.manage_gaws.start()

    @tasks.loop(seconds=20)
    async def manage_gaws(self):
        with open("json_files/giveaways.json", "r") as g:
            gaws = json.load(g)
        db['giveaways'] = gaws
        keys = list(gaws.keys())
        keys.reverse()
        for gaw in keys:
            with open("json_files/giveaways.json", "r") as g:
                gaws = json.load(g)
            try:
                data = gaws[gaw]
                ends = datetime.strptime(data["endtime"], "%m/%d/%Y, %H:%M:%S")
                if (ends + timedelta(days=14)) < datetime.now():
                    gaws.pop(gaw)
                    with open("json_files/giveaways.json", "w") as g:
                        json.dump(gaws, g, indent=4)
                if ends < datetime.now() and data["ended"] is False:
                    data["ended"] = True
                    

                    ####

                    try:
                        reroll = False
                        data.pop("role")
                        data.pop("messages")
                        data.pop("level")
                    except KeyError:
                        reroll = True
                    gaws[gaw] = data
                    with open("json_files/giveaways.json", "w") as g:
                        json.dump(gaws, g, indent=4)
                    try:
                        member = await self.client.fetch_user(data["author"])
                        channel = await self.client.fetch_channel(data["channel"])
                        msg = await channel.fetch_message(int(gaw))
                        potwinners = []
                        try:
                            await msg.remove_reaction("🎉", self.client.user)
                        except Exception:
                            pass
                        for reaction in msg.reactions:
                            if reaction.emoji == "🎉":
                                potwinners = await reaction.users().flatten()
                                break
                        count = data["winners"]
                        winners = None
                        if count == 0:
                            await channel.send(
                                f"**Nobody** won the giveaway for **{data['name']}!** :smirk:"
                            )
                        elif len(potwinners) == 0:
                            await channel.send(
                                f"Could not determine a winner for the giveaway for **{data['name']}.** :confused:"
                            )
                        else:
                            if len(potwinners) < data["winners"]:
                                count = len(potwinners)
                            winnerlist = random.choices(potwinners, k=count)
                            i = 0
                            embed = discord.Embed(
                                description=f"You won the [giveaway for {data['name']}]({msg.jump_url}).\nContact <@{data['author']}> for the prizes",
                                color=discord.Colour.green(),
                            )
                            embed.set_author(name="🥳 You won!")
                            for winner in winnerlist:
                                try:
                                    dmchannel = await winner.create_dm()
                                    await dmchannel.send(None, embed=embed)
                                except Exception:
                                    pass
                                winnerlist[i] = winner.mention
                                i += 1
                            winners = ", ".join(winnerlist)
                            await channel.send(
                                f"Congratulations {winners}, you won **{data['name']}!** :partying_face:\nContact <@{data['author']}> for the prizes."
                            )
                        embed = discord.Embed(
                            title=data["name"],
                            description=f"Hosted by <@{data['author']}>\nWinners: {winners}",
                            color=discord.Colour.random(),
                            timestamp=ends,
                        )
                        if reroll is True:
                            embed.set_author(name="🔄 Rerolled Giveaway", icon_url=member.avatar_url)
                        else:
                            embed.set_author(name="🎊 Ended Giveaway", icon_url=member.avatar_url)
                        embed.set_footer(text="Ended at")
                        try:
                            await msg.edit(content=None, embed=embed)
                        except Exception:
                            pass
                        embed = discord.Embed(
                            description=f"You have the following winners:\n{winners}\n\n[Click here to jump directly to your giveaway.]({msg.jump_url})",
                            color=discord.Colour.teal(),
                        )
                        if reroll is True:
                            embed.set_author(name="🔄 Your giveaway has been rerolled")
                            embed.set_footer(text="You will be able to reroll it again for 14 days.")
                        else:
                            embed.set_author(name="🎉 Your giveaway has ended")
                            embed.set_footer(text="You will be able to reroll it for 14 days.")
                        try:
                            channel = await member.create_dm()
                            await channel.send(embed=embed)
                        except Exception:
                            pass
                    except Exception:
                        pass
            except Exception:
                pass
            db['giveaways'] = gaws

    @cog_ext.cog_slash(
        name="giveaway",
        description="Creates a neat giveaway!",
        options=[
            dict(
                name="prize",
                description="What's your prize for your giveaway?",
                type=3,
                required="true",
            ),
            dict(
                name="duration",
                description="How long do you want your giveaway to last?",
                type=3,
                required="true",
            ),
            dict(
                name="winners",
                description="How many winners do you want?",
                type=4,
                required="true",
            ),
            dict(
                name="channel",
                description="What channel do you want your giveaway to be in?",
                type=7,
                required="true",
            ),
            dict(
                name="role",
                description="Is there a role users need?",
                type=8,
                required="false",
            ),
            dict(
                name="messages",
                description="How many messages do members need?",
                type=4,
                required="false",
            ),
            dict(
                name="invites",
                description="How many users do members need to have invited?",
                type=4,
                required="false",
            ),
            dict(
                name="server",
                description="Is there a server users need to be in? Send its name, its id or an invite link to it!",
                type=3,
                required="false",
            ),
            dict(
                name="level",
                description="What TimMcBot level do members need?",
                type=4,
                required="false",
            ),
        ],
    )
    async def _create_giveaway(
        self,
        ctx,
        prize,
        duration,
        winners,
        channel,
        role=None,
        messages=None,
        invites=None,
        server=None,
        level=None,
    ):
        string_duration = duration
        required_role = role
        required_messages = messages
        required_invites = invites
        required_server = server
        required_level = level
        keys = [
            "name",
            "endtime",
            "winners",
            "channel",
            "role",
            "messages",
            "level",
            "author",
        ]

        await ctx.defer()

        if not str(channel.type) == "text":
            await ctx.send(embed=discord.Embed(title="Error", description="The selected channel isn't a text channel!", color=discord.Color.red()))
            return
            
        data = {}
        data["name"] = prize

        # get end time
        try:
            element, duration = "", timedelta()
            for i in string_duration:
                if i.isnumeric():
                    element = f"{element}{i}"
                elif not element == "":
                    element = int(element)
                    if i == "w":
                        duration = duration + timedelta(weeks=element)
                    elif i == "d":
                        duration = duration + timedelta(days=element)
                    elif i == "h":
                        duration = duration + timedelta(hours=element)
                    elif i == "m":
                        duration = duration + timedelta(minutes=element)
                    elif i == "s":
                        duration = duration + timedelta(seconds=element)
                    element = ""
            if duration == timedelta():
                await ctx.send(
                    embed=discord.Embed(
                        description="**You didn't enter a valid duration. Please try again!**\nEnter the duration like that:\n```glsl\n3 weeks = 3w\n1 day and 20 hours = 1d, 20h\n30 minutes and 10 seconds = 30m, 10s``` ",
                        color=discord.Colour.red(),
                    )
                )
                return
        except OverflowError:
            await ctx.send(
                embed=discord.Embed(
                    title="Overflow Error",
                    description="The values you entered for the duration of your giveaway are **too big.**\n\nPlease try again!",
                    color=discord.Colour.red(),
                )
            )
            return
        except Exception:
            await ctx.send(
                embed=discord.Embed(
                    description="**Something went wrong.** Please try again!",
                    color=discord.Colour.red(),
                )
            )
            return
        data["endtime"] = (datetime.now() + duration).strftime("%m/%d/%Y, %H:%M:%S")

        if not 0 <= winners < 100:
            await ctx.send(
                embed=discord.Embed(
                    description="**A giveaway can only have between 0 and 99 winners. Please try again!**",
                    color=discord.Colour.red(),
                )
            )
            return
        data["winners"] = winners
        data["channel"] = channel

        perms = channel.permissions_for(ctx.author)
        if perms.send_messages is False or perms.view_channel is False:
            await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="You are **not allowed to create giveaways in this channel** because you can't send messages there!",
                    color=discord.Colour.red(),
                )
            )
            return

        data["role"] = required_role
        data["messages"] = required_messages
        data["invites"] = required_invites
        data["guild"] = None

        if not required_server is None and not (
            required_server.lower() == "skip" or required_server.lower() == "none" or required_server.lower() == "no"
        ):
            try:
                try:
                    guild_id = int(required_server)
                except Exception:
                    invite = await self.client.fetch_invite(required_server)
                    guild = invite.guild
                    if isinstance(guild, discord.PartialInviteGuild):
                        embed = discord.Embed(
                            description="You can only set a server as requirement if TimMcBot is in it!\n\nPlease [add TimMcBot to the server](https://discord.com/api/oauth2/authorize?client_id=800377812699447306&permissions=4294967287&scope=bot%20applications.commands) or choose another one.",
                            color=discord.Colour.red(),
                        )
                        embed.set_author(
                            name=f"TimMcBot isn't in '{guild.name}'",
                            icon_url=str(guild.icon_url),
                        )
                        await ctx.send(embed=embed)
                        return
                    data["guild"] = guild
                else:
                    guild = await self.client.fetch_guild(guild_id)
                    data["guild"] = guild
            except Exception:
                guild = discord.utils.get(self.client.guilds, name=required_server)
                if guild is None:
                    await ctx.send(
                        embed=discord.Embed(
                            description="**Couldn't fetch the server you set as requirement.** Please try again!",
                            color=discord.Colour.red(),
                        )
                    )
                    return
                else:
                    data["guild"] = guild

        data["level"] = required_level

        data["author"] = ctx.author.id

        await create_giveaway(self, ctx, data)

    @commands.command(
        help="If you have permission to use slash commands, you can also use type `/giveaway`!",
        brief="Create a neat giveaway",
        description="Starts the process to create a giveaway.",
        aliases=["giveaway", "gstart"],
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def gcreate(self, ctx):
        embed = discord.Embed(
            title="Please answer the questions",
            description=f"You have **5 minutes** for each question.\nYou can stop the process anytime by typing **`cancel`**",
            color=discord.Colour.green(),
        )
        embed.set_author(name="🎁 Create a giveaway", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

        await create_giveaway(self, ctx)

    @cog_ext.cog_subcommand(
        base="gw",
        name="end",
        description="Ends one of your running giveaways early.",
        options=[
            dict(
                name="giveaway_message_id",
                description="The message id of the giveaway you want to end.",
                type=3,
                required="true",
            )
        ],
    )
    @commands.check(is_not_private)
    async def _end_giveaway(self, ctx, giveaway_message_id):
        await end(self, ctx, giveaway_message_id, slash=True)

    @commands.command(
        brief="Ends a giveaways early",
        description="Allows you to end one of your giveaways early. The giveaway must be hosted by you.",
    )
    async def end(self, ctx, giveaway_message_id):
        prefix = get_prefix(self.client, ctx.message)[1]
        await end(self, ctx, giveaway_message_id, prefix=prefix)

    @cog_ext.cog_subcommand(
        base="gw",
        name="cancel",
        description="Cancels one of your running giveaways.",
        options=[
            dict(
                name="giveaway_message_id",
                description="The message id of the giveaway you want to cancel.",
                type=3,
                required="true",
            )
        ],
    )
    @commands.check(is_not_private)
    async def _cancel_giveaway(self, ctx, giveaway_message_id):
        await cancel(self, ctx, giveaway_message_id, slash=True)

    @commands.command(
        brief="Cancels a giveaway",
        description="Allows you to cancel one of your giveaways. The giveaway must be hosted by you.",
    )
    async def cancel(self, ctx, giveaway_message_id):
        await cancel(self, ctx, giveaway_message_id)

    @cog_ext.cog_subcommand(
        base="gw",
        name="reroll",
        description="Rerolls one of your ended giveaways.",
        options=[
            dict(
                name="giveaway_message_id",
                description="The message id of the giveaway you want to reroll.",
                type=3,
                required="false",
            )
        ],
    )
    @commands.check(is_not_private)
    async def _reroll_giveaway(self, ctx, giveaway_message_id=None):
        await reroll(self, ctx, giveaway_message_id, slash=True)

    @commands.command(
        brief="Rerolls a giveaway",
        description="Allows you to let the bot pick new winners for one of your ended giveaways. The giveaway must be hosted by you.\nIf you don't provide a message id, your latest giveaway in the channel will be rerolled.",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def reroll(self, ctx, giveaway_message_id=None):
        await reroll(self, ctx, giveaway_message_id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) == "🎉":
            with open("json_files/giveaways.json", "r") as g:
                gaws = json.load(g)
            with open("json_files/leveling.json", "r") as d:
                servers = json.load(d)
            if str(payload.message_id) in gaws:
                data = gaws[str(payload.message_id)]
                channel = await self.client.fetch_channel(payload.channel_id)
                guild = channel.guild
                member = await guild.fetch_member(payload.user_id)
                if not member.bot:
                    message = await channel.fetch_message(payload.message_id)
                    reactions = message.reactions
                    if data["ended"]:
                        try:
                            await join_failure(
                                member,
                                reactions,
                                text="This giveaway already ended!",
                                url=message.jump_url,
                            )
                            return
                        except Exception:
                            return
                    if data["author"] == member.id:
                        try:
                            await join_failure(
                                member,
                                reactions,
                                text="You can't join your own giveaways!",
                                url=message.jump_url,
                            )
                            return
                        except Exception:
                            return
                    if not data["role"] is None:
                        try:
                            role = guild.get_role(data["role"])
                        except Exception:
                            return
                        if not role in (member.roles):
                            try:
                                await join_failure(
                                    member,
                                    reactions,
                                    text=f"You don't have the **`{role.name}`** role which is required to join [this]({message.jump_url}) giveaway",
                                    url=message.jump_url,
                                )
                                return
                            except Exception:
                                return
                    if not data["messages"] is None:
                        try:
                            if (
                                servers[str(guild.id)][str(member.id)]["messages"]
                                < data["messages"]
                            ):
                                try:
                                    await join_failure(
                                        member,
                                        reactions,
                                        text=f"You don't have enough message!\n```Required messages: {data['messages']}\nYour message count: {servers[str(guild.id)][str(member.id)]['messages']}```",
                                        url=message.jump_url,
                                    )
                                    return
                                except Exception:
                                    return
                        except KeyError:
                            try:
                                await join_failure(
                                    member,
                                    reactions,
                                    text=f"You don't have enough message!\n```Required messages: {data['messages']}\nYour message count: 0```",
                                    url=message.jump_url,
                                )
                                return
                            except Exception:
                                return
                    if not data["level"] is None:
                        try:
                            xp = servers[str(guild.id)][str(member.id)]["xp"]
                            level = leveling.getlevel(xp)[0]
                            if level < data["level"]:
                                try:
                                    await join_failure(
                                        member,
                                        reactions,
                                        text=f"Your level isn't high enough!\n```Required level: {data['level']}\nYour TimMcBot level: {level}```",
                                        url=message.jump_url,
                                    )
                                    return
                                except Exception:
                                    return
                        except KeyError:
                            try:
                                await join_failure(
                                    member,
                                    reactions,
                                    text=f"Your level isn't high enough!\n```Required level: {data['level']}\nYour TimMcBot level: None```",
                                    url=message.jump_url,
                                )
                                return
                            except Exception:
                                return
                    if not data["guild"] is None:
                        try:
                            required_guild = await self.client.fetch_guild(
                                data["guild"]
                            )
                            try:
                                await required_guild.fetch_member(member.id)
                            except Exception:
                                try:
                                    await join_failure(
                                        member,
                                        reactions,
                                        text=f"You have to be in the server **`{required_guild.name}`** to join [this]({message.jump_url}) giveaway",
                                        url=message.jump_url,
                                    )
                                    return
                                except Exception:
                                    return
                        except Exception:
                            pass
                    if not data["invites"] is None:
                        try:
                            invites = await guild.invites()
                            invited_users = 0
                            for invite in invites:
                                if invited_users >= data["invites"]:
                                    break
                                if invite.inviter.id == member.id:
                                    invited_users += invite.uses
                            if not invited_users >= data["invites"]:
                                try:
                                    await join_failure(
                                        member,
                                        reactions,
                                        text=f"Your didn't invite enough users to the server!\n```Required: {data['invites']} users\nYou invited: {invited_users} users```",
                                        url=message.jump_url,
                                    )
                                    return
                                except Exception:
                                    return
                        except Exception:
                            pass

async def end(self, ctx, giveaway_message_id, *, prefix="/gw ", slash=False):
    with open("json_files/giveaways.json", "r") as g:
        gaws = json.load(g)
    if giveaway_message_id in gaws:
        data = gaws[giveaway_message_id]
        if data["author"] == ctx.author.id:
            if data["ended"] is True:
                error = f"That giveaway **already ended!** :confetti_ball: To reroll giveaways, use `{prefix}reroll <giveaway_message_id>`."
            else:
                if slash is True:
                    await ctx.defer()
                data["endtime"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                gaws[giveaway_message_id] = data

                db['giveaways'] = gaws
                with open("json_files/giveaways.json", "w") as g:
                    json.dump(gaws, g, indent=4)
                self.manage_gaws.restart()
                if slash is True:
                    await ctx.send("👌 alright, the giveaway will be ended!")
                else:
                    await ctx.message.add_reaction(emojis["checkmark"])
                return
        else:
            error = "That giveaway was **hosted by someone else!** You can't end other's giveaways."
    else:
        error = "Couldn't find your giveaway! Please make sure you entered the **correct message id.**"
    if slash is True:
        await ctx.send(error, hidden=True)
    else:
        await ctx.send(error)

async def reroll(self, ctx, giveaway_message_id, *, slash=False):
    with open("json_files/giveaways.json", "r") as g:
        gaws = json.load(g)
    if giveaway_message_id is None:
        keys = list(gaws.keys())
        keys.reverse()
        for key in keys:
            if (
                gaws[key]["author"] == ctx.author.id
                and gaws[key]["ended"] is True
                and gaws[key]["channel"] == ctx.channel.id
            ):
                giveaway_message_id = key
                break
    if giveaway_message_id is None:
        if slash is True:
            await ctx.send("Couldn't find any giveaways to reroll in here!", hidden=True)
        else:
            await ctx.send("Couldn't find any giveaways to reroll in here!")
        return
    if giveaway_message_id in gaws:
        data = gaws[giveaway_message_id]
        if data["author"] == ctx.author.id:
            if data["ended"] is True:
                if "url" in data:
                    embed = discord.Embed(
                        description=f"Are you sure you want to reroll [this]({data['url']}) giveaway?",
                        color=get_client_color(ctx),
                    )
                else:
                    embed = discord.Embed(
                        description=f"Are you sure you want to reroll [this](https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{giveaway_message_id}) giveaway?",
                        color=get_client_color(ctx),
                    )
                embed.set_author(
                    name="🔄 Giveaway Reroll", icon_url=ctx.author.avatar_url
                )
                reminder = await ctx.send(embed=embed)
                if slash is True:
                    reminder = ctx.message

                await reminder.add_reaction("✅")
                await reminder.add_reaction("❌")

                def check(reaction, user):
                    return (
                        reaction.message.id == reminder.id
                        and user.id == ctx.author.id
                        and not user.bot
                        and str(reaction.emoji) in ["✅", "❌"]
                    )

                try:
                    reaction, user = await self.client.wait_for(
                        "reaction_add", timeout=30, check=check
                    )
                except asyncio.TimeoutError:
                    if slash is True:
                        await ctx.send("You didn't react in time.")
                    await reminder.edit(
                        content=None,
                        embed=discord.Embed(
                            title=":alarm_clock: Timeout", color=discord.Colour.red()
                        ),
                    )
                    await reminder.clear_reactions()
                else:
                    if str(reaction.emoji) == "❌":
                        await ctx.channel.send("👌 ok, the giveaway won't be rerolled then.")
                    if str(reaction.emoji) == "✅":
                        await ctx.channel.send("👌 alright, the giveaway will be rerolled!")
                        data["ended"] = False
                        gaws.pop(giveaway_message_id)
                        gaws[giveaway_message_id] = data

                        db['giveaways'] = gaws
                        with open("json_files/giveaways.json", "w") as g:
                            json.dump(gaws, g, indent=4)
                        self.manage_gaws.restart()
                return
            else:
                error = f"That giveaway **hasn't ended yet! 🎁** You can only reroll ended giveaways."
        else:
            error = "That giveaway was **hosted by someone else!** You can't reroll other's giveaways."
    else:
        error = "Couldn't find your giveaway! Please make sure that you entered the **correct message id.**"
    if slash is True:
        await ctx.send(error, hidden=True)
    else:
        await ctx.send(error)

async def cancel(self, ctx, giveaway_message_id, slash=False):
    with open("json_files/giveaways.json", "r") as g:
        gaws = json.load(g)
    if giveaway_message_id in gaws:
        data = gaws[giveaway_message_id]
        if data["author"] == ctx.author.id:
            if data["ended"] is True:
                error = "That giveaway **already ended!** :confetti_ball: You can't cancel it anymore."
            else:
                if slash is True:
                    await ctx.defer()
                channel = await self.client.fetch_channel(data["channel"])
                gaws.pop(giveaway_message_id)

                db['giveaways'] = gaws
                with open("json_files/giveaways.json", "w") as g:
                    json.dump(gaws, g, indent=4)
                message = await channel.fetch_message(int(giveaway_message_id))
                await message.edit(
                    embed=discord.Embed(
                        title="This giveaway was cancelled.",
                        color=discord.Color.red(),
                    )
                )
                await message.clear_reactions()
                embed = discord.Embed(
                    description=f"The giveaway for **{data['name']}** has been cancelled.",
                    color=discord.Color.random(),
                )
                embed.set_author(
                    name="✖ Giveaway cancelled", icon_url=ctx.author.avatar_url
                )
                if slash is False:
                    await ctx.message.add_reaction(emojis["checkmark"])
                await ctx.send(embed=embed)
                return
        else:
            error = "That giveaway was **hosted by someone else!** You can't cancel other's giveaways."
    else:
        error = "Couldn't find your giveaway! Please make sure you entered the **correct message id.**"
    if slash is True:
        await ctx.send(error, hidden=True)
    else:
        await ctx.send(error)

async def join_failure(member, reactions, *, text, url=None):
    for item in reactions:
        if str(item.emoji) == "🎉":
            await item.remove(member)
            break
    channel = await member.create_dm()
    embed = discord.Embed(description=text, color=discord.Colour.red())
    embed.set_author(name="⚠️ You cannot join this giveaway")
    await channel.send(embed=embed)


# activate cogs


def setup(client):
    client.add_cog(giveaways(client))
