import discord
import random
from random import randint
from discord.ext import commands, tasks
from main import assets, emojis, get_prefix, is_not_private, get_client_color
import asyncio
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from dhooks import Webhook
from PIL import Image, ImageFilter, ImageEnhance
import requests
import os

rickroll_wins = [
    "LOTS OF MONEY",
    "Discord Nitro",
    "Discord Nitro",
    ":candy: free candy",
    "Nitro Classic",
]

# cogs


class fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    # commands

    @commands.command()
    async def blur(self, ctx, user: discord.User=None, intensity: int=4):
        if user is None:
            user = ctx.author

        img = requests.get(str(user.avatar_url_as(size=128)), allow_redirects=True)
        open(f'temp_files/{user.id}avatar.png', 'wb').write(img.content)

        filtered_img = Image.open(f'temp_files/{user.id}avatar.png').filter(ImageFilter.GaussianBlur(intensity))
        filtered_img.save(f'temp_files/blur{user.id}avatar.png')

        await ctx.send(file=discord.File(f'temp_files/blur{user.id}avatar.png'))

        os.remove(f'temp_files/{user.id}avatar.png')
        os.remove(f'temp_files/blur{user.id}avatar.png')

    @commands.command()
    async def test(self, ctx, user: discord.User=None):
        if user is None:
            user = ctx.author

        img = requests.get(str(user.avatar_url_as(size=128)), allow_redirects=True)
        open(f'temp_files/{user.id}avatar.png', 'wb').write(img.content)

        filtered_img = Image.open(f'temp_files/{user.id}avatar.png').filter(ImageEnhance.Contrast(5))

        filtered_img.save(f'temp_files/blur{user.id}avatar.png')

        await ctx.send(file=discord.File(f'temp_files/blur{user.id}avatar.png'))

        os.remove(f'temp_files/{user.id}avatar.png')
        os.remove(f'temp_files/blur{user.id}avatar.png')

    @commands.command()
    async def blobchain(self, ctx):
        blobs = randint(1, 16)
        blobchain = ""
        for i in range(0, blobs):
            blobchain = f"{blobchain}{emojis['blobchain']}"
        await ctx.send(blobchain)

    @commands.command(
        aliases=["die", "würfel", "würfeln"],
        brief="Rolls the dice",
        description="Rolls the dice.",
    )
    async def dice(self, ctx):
        zahlen = ["one", "two", "three", "four", "five", "six"]
        if ctx.author.nick == None:
            user = ctx.author.name
        else:
            user = ctx.author.nick
        if randint(0, 6) == 6:
            await ctx.send(
                embed=discord.Embed(
                    description=f"☹ **{user} wanted to roll their dice, but then realized that they forgot it at home!** rip",
                    color=discord.Colour.random(),
                )
            )
        else:
            await ctx.send(
                embed=discord.Embed(
                    description=f"🎲 **{user} rolled a {random.choice(zahlen)}!**",
                    color=discord.Colour.random(),
                )
            )

    @commands.command(aliases=["f-in-the-chat", "f"])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def pressf(self, ctx, *, occurrence):
        message = await ctx.send(
            f"**{occurrence}** - React with {emojis['f_in_the_chat']} to pay respects!"
        )
        await message.add_reaction(emojis["f_in_the_chat"])
        reactions = 0
        reactors = []

        def check(reaction, user):
            return (
                reaction.message == message
                and not user.bot
                and str(reaction.emoji) == emojis["f_in_the_chat"]
            )

        while True:
            try:
                reaction, user = await self.client.wait_for(
                    "reaction_add", timeout=300.0, check=check
                )
            except asyncio.TimeoutError:
                if reactions == 0:
                    await ctx.send(
                        "Time's up! :alarm_clock: **Nobody** paid their respects. :slight_frown:"
                    )
                else:
                    await ctx.send(
                        f"Time's up! :alarm_clock: The following people paid their respects: **{', '.join(reactors)}**"
                    )
                return
            else:
                reactions += 1
                if user.name in reactors:
                    await ctx.send(
                        f"{user.mention} paid their respects **again!** {emojis['f_in_the_chat']} They seem to be really compassionate ..."
                    )
                else:
                    reactors.append(user.name)
                    await ctx.send(
                        f"{user.mention} paid their respects! {emojis['f_in_the_chat']}"
                    )

    @cog_ext.cog_slash(
        name="hardcore-spoiler",
        description="Adds a very unique hardcore spoilers to your message!",
        options=[
            dict(
                name="message",
                description="Your message goes here",
                type=3,
                required="true",
            )
        ],
    )
    @commands.check(is_not_private)
    async def _hardcorespoiler(self, ctx, message):
        await ctx.send(await hardcore_spoiler(ctx, message))

    @commands.command(name="harcore-spoiler", aliases=["hardcorespoiler"])
    async def hardcorespoiler(self, ctx, *, text=None):
        await ctx.message.delete()
        await ctx.send(await hardcore_spoiler(ctx, text))
        webhook = await ctx.channel.create_webhook(
            name=ctx.channel.id,
            reason="A slash command that requires a webhook was run",
        )
        spoilered = await hardcore_spoiler(ctx, message)
        if ctx.author.nick is None:
            await webhook.send(
                spoilered, username=ctx.author.name, avatar_url=ctx.author.avatar_url
            )
        else:
            await webhook.send(
                spoilered, username=ctx.author.nick, avatar_url=ctx.author.avatar_url
            )
        await webhook.delete()

    @cog_ext.cog_slash(
        name="rickroll",
        description="You'll see what it does ;)",
        options=[
            dict(
                name="target",
                description="If you want to rickroll a specific member, mention it now!",
                type=6,
                required="false",
            )
        ],
    )
    async def _rickroll(self, ctx, target=None):
        if target is None:
            await ctx.send(
                "https://media.tenor.com/images/59de4445b8319b9936377ec90dc5b9dc/tenor.gif"
            )
        else:
            await ctx.send(
                f"{target.mention} {ctx.author.name} has gifted you **{random.choice(rickroll_wins)}!** :tada:",
                embed=discord.Embed(
                    description="**[Click here to claim it!](http://alturl.com/7y5we)** :boom:",
                    color=discord.Colour.blue(),
                ),
            )

    @commands.command(
        brief="You'll see what it does ;)",
        description="Gifts a member something cool! ~~actually rickrolls them~~",
        aliases=["prank"],
    )
    async def rickroll(self, ctx, target: discord.Member):
        await ctx.message.delete()
        await ctx.send(
            f"{target.mention} {ctx.author.name} has gifted you **{random.choice(rickroll_wins)}!** :tada:",
            embed=discord.Embed(
                description="**[Click here to claim it!](http://alturl.com/7y5we)** :boom:",
                color=discord.Colour.blue(),
            ),
        )

    @commands.Cog.listener()
    @rickroll.error
    async def rickroll_mrq(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.send("You gotta mention someone to ||rickroll||. :eyes:")

    @commands.command()
    async def clap(self, ctx, *, text=None):
        if text == None:
            await ctx.send("What am I supposed to say?")
            return
        output = ""
        o = 0
        for i in text:
            o = o + 1
            if o == len(text):
                output = f"{output}{i}"
            else:
                output = f"{output}{i}  :clap: "
        await ctx.send(output)

    @commands.command(aliases=["backwards", "umgedreht"])
    async def reverse(self, ctx, *, text=None):
        if text == None:
            await ctx.send("Please also enter a text so I can esrever it!")
            return
        output = ""
        for i in text:
            if not i == "|":
                output = f"{i}{output}"
        if "@everyone" in output or "@here" in output:
            await ctx.send("STOP PINGING! :angry:")
        elif "<@&" in output:
            await ctx.send(
                "Please try again, but without pinging roles this time. :ping_pong:"
            )
        else:
            await ctx.send(output)

    @cog_ext.cog_slash(
        name="emojify",
        description="🇪 🇲 🇴 🇯 🇮 🇫 🇮 🇪 🇸 your message.",
        options=[
            dict(
                name="message",
                description="Your message goes here",
                type=3,
                required="true",
            )
        ],
    )
    @commands.check(is_not_private)
    async def _emojify(self, ctx, message):
        await ctx.send(await emojify(ctx, message))

    @commands.command(brief="Emojifies your message")
    async def emojify(self, ctx, *, text=None):
        await ctx.message.delete()
        webhook = await ctx.channel.create_webhook(
            name=ctx.channel.id,
            reason="A slash command that requires a webhook was run",
        )
        emojified = await emojify(ctx, text)
        if ctx.author.nick is None:
            await webhook.send(
                emojified, username=ctx.author.name, avatar_url=ctx.author.avatar_url
            )
        else:
            await webhook.send(
                emojified, username=ctx.author.nick, avatar_url=ctx.author.avatar_url
            )
        await webhook.delete()

    @commands.command(name="8ball", aliases=["ask"])
    async def eightball(self, ctx, *, question=None):
        options = [
            # yes
            "As I see it, yes.",
            ":thumbsup:",
            "Yes",
            "Most likely.",
            "YESSSSSSSS!!!",
            "Without a doubt.",
            # no
            "No - definitely not.",
            ":thumbsdown:",
            "I don't think so.",
            "No",
            "Nope",
            "My reply is no.",
            # others
            "Cannot predict now.",
            "Maybe",
            "idk",
            "I'm confused. :confused:",
            "Go and ask someone else.",
            "Better not tell you now.",
            "I won't ever tell you :laughing:",
            "Concentrate and ask again.",
            "I'm tired. :sleeping: Please ask me again later.",
        ]
        if question == None:
            await ctx.send("You didn't ask anything. :thinking:")
        elif "@everyone" in question or "@here" in question:
            await ctx.send("STOP PINGING! :angry:")
        elif "<@&" in question:
            await ctx.send(
                "Please try again, but without pinging roles this time. :ping_pong:"
            )
        else:
            await ctx.send(
                f"**Question:** {question} \n**Answer:** {random.choice(options)}"
            )


async def hardcore_spoiler(ctx, text):
    if text == None:
        await ctx.send(
            "Please also enter a text so I can write it with ||S||||p||||o||||i||||l||||e||||r||||s||!"
        )
        return
    output = ""
    for i in text:
        if not i == "|":
            output = f"{output}||{i}||"
    return output


async def emojify(ctx, text):
    if text == None:
        await ctx.send(
            "Please also enter a text so I can :regional_indicator_e: :regional_indicator_m: :regional_indicator_o: :regional_indicator_j: :regional_indicator_i: :regional_indicator_f: :regional_indicator_y: it!"
        )
        return
    output = ""
    symbols = {"$": ":heavy_dollar_sign:", "!": ":exclamation:", "?": ":question:"}
    alpha = True
    for i in text:
        if i.isalpha():
            o = i.lower()
            output = f"{output}:regional_indicator_{o}: "
        elif i == " ":
            output = f"{output}  "
        elif i in symbols:
            output = f"{output}{symbols[i]} "
        else:
            try:
                item = int(i)
                numemojis = [
                    ":zero:",
                    ":one:",
                    ":two:",
                    ":three:",
                    ":four:",
                    ":five:",
                    ":six:",
                    ":seven:",
                    ":eight:",
                    ":nine:",
                ]
                output = f"{output}{numemojis[item]} "
            except ValueError:
                output += i + " "
    return output


# activate cogs


def setup(client):
    client.add_cog(fun(client))
