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
    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(1, 2.7, commands.BucketType.user)
    async def blur(self, ctx, *, user: discord.User=None):
        if user is None:
            user = ctx.author

        img = requests.get(user.avatar_url, allow_redirects=True)
        open(f'temp_files/blur{user.id}.png', 'wb').write(img.content)

        filtered_img = Image.open(f'temp_files/blur{user.id}.png').filter(ImageFilter.GaussianBlur(12))
        filtered_img.save(f'temp_files/blur{user.id}.png')

        await ctx.send(file=discord.File(f'temp_files/blur{user.id}.png'))

        os.remove(f'temp_files/blur{user.id}.png')

    @commands.command(aliases=["colourful"])
    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(1, 2.7, commands.BucketType.user)
    async def colorful(self, ctx, *, user: discord.User=None):
        if user is None:
            user = ctx.author

        img = requests.get(user.avatar_url, allow_redirects=True)
        open(f'temp_files/color{user.id}.png', 'wb').write(img.content)

        filtered_img = ImageEnhance.Color(Image.open(f'temp_files/color{user.id}.png'))

        filtered_img.enhance(20.0).save(f'temp_files/color{user.id}.png')

        await ctx.send(file=discord.File(f'temp_files/color{user.id}.png'))

        os.remove(f'temp_files/color{user.id}.png')

    @commands.command(aliases=["blend"])
    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def merge(self, ctx, user1 : discord.User, user2: discord.User):
        await merge(self, ctx, user1, user2)

    '''
    @cog_ext.cog_slash(
        name="blobchain",
        description="Displays a very colorful chain of blobs",
    )
    async def _blobchain(self, ctx):
        blobs = randint(1, 16)
        blobchain = ""
        for i in range(0, blobs):
            blobchain = f"{blobchain}{emojis['blobchain']}"
        await ctx.send(blobchain)  '''      

    @commands.command(hidden=True)
    @commands.bot_has_permissions(use_external_emojis=True)
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
        if randint(0, 6) == 6:
            await ctx.send(
                embed=discord.Embed(
                    description=f"☹ **{ctx.author.display_name} wanted to roll their dice, but then realized that they forgot it at home!** rip",
                    color=discord.Colour.random(),
                )
            )
        else:
            await ctx.send(
                embed=discord.Embed(
                    description=f"🎲 **{ctx.author.display_name} rolled a {random.choice(zahlen)}!**",
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
                reaction.message.id == message.id
                and not user.bot
                and str(reaction.emoji) == emojis["f_in_the_chat"]
            )

        while True:
            try:
                reaction, user = await self.client.wait_for(
                    "reaction_add", timeout=30.0, check=check
                )
            except asyncio.TimeoutError:
                if reactions == 0:
                    await message.reply(
                        "Time's up! :alarm_clock: **Nobody** paid their respects. :slight_frown:"
                    )
                else:
                    await message.reply(
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

    @commands.command(name="spoiler", aliases=["spoilered", "harcore-spoiler","hardcorespoiler"])
    async def hardcorespoiler(self, ctx, *, text):
        await ctx.message.delete()
        spoilered = await hardcore_spoiler(ctx, text)
        if spoilered is None:
            return
        await ctx.send(spoilered)

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
    @commands.bot_has_permissions(manage_messages=True)
    async def rickroll(self, ctx, target: discord.Member=None):
        await ctx.message.delete()
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

    @commands.command()
    async def clap(self, ctx, *, text):
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
    async def reverse(self, ctx, *, text):
        output = "".join(reversed(text))
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
    async def emojify(self, ctx, *, text):
        emojified = await emojify(ctx, text)
        if emojified is None:
            return
        await ctx.message.reply(emojified)

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
        if "@everyone" in question or "@here" in question:
            await ctx.message.reply("**The magic 🎱 says:**\n> STOP PINGING! :angry:")
        else:
            await ctx.message.reply(
                f"**The magic 🎱 says:**\n> {random.choice(options)}"
            )


async def hardcore_spoiler(ctx, text):
    output = ""
    for i in text:
        if not i == "|":
            output = f"{output}||{i}||"
    return output


async def emojify(ctx, text):
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

async def merge(self, ctx, user1, user2):
    image1 = requests.get(user1.avatar_url, allow_redirects=True)
    open(f'temp_files/merge{user1.id}.png', 'wb').write(image1.content)
    image1 = Image.open(f'temp_files/merge{user1.id}.png').convert('RGB').resize((1024,1024))

    os.remove(f'temp_files/merge{user1.id}.png')

    image2 = (requests.get(user2.avatar_url, allow_redirects=True))
    open(f'temp_files/merge{user2.id}.png', 'wb').write(image2.content)
    image2 = Image.open(f'temp_files/merge{user2.id}.png').convert('RGB').resize((1024,1024))

    os.remove(f'temp_files/merge{user2.id}.png')

    blended = Image.blend(image1, image2, alpha=0.5)
    blended.save(f'temp_files/merge{user1.id}&{user2.id}.png')

    await ctx.send(file=discord.File(f'temp_files/merge{user1.id}&{user2.id}.png'))

    os.remove(f'temp_files/merge{user1.id}&{user2.id}.png')

# activate cogs


def setup(client):
    client.add_cog(fun(client))
