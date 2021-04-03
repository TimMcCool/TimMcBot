import discord
import random
from random import randint
from discord.ext import commands, tasks
from main import assets, emojis, get_prefix, is_not_private, get_client_color
import asyncio
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from dhooks import Webhook
import json
from datetime import datetime
import requests

# cogs


class globalchat(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.user_cooldown = {}

    # commands

    @commands.Cog.listener()
    async def on_message(self, message):
        with open("json_files/globalchat.json", "r") as g:
            gchannels = json.load(g)   
        if str(message.channel.id) in gchannels and not message.author.bot is True:
            try:
                embed = discord.Embed(
                    title="New Message",
                    description=message.content,
                    color=discord.Color.random(),
                    timestamp=datetime.now()
                )
                embed.set_author(name=f"🌍 Global Chat by TimMcBot")
                embed.set_thumbnail(url=message.author.avatar_url)
                embed.set_footer(text=f"Server: {message.guild.name} | {message.guild.id}", icon_url=message.guild.icon_url)
                Webhook(gchannels[str(message.channel.id)]).send(embed=embed, username=str(message.author), avatar_url=str(message.author.avatar_url))
            except requests.exceptions.HTTPError:
                await message.channel.send(embed=discord.Embed(title="Error", description="The webhook was not found in this channel! **Therefore, the global chat has been removed.**\nIf you want to add it again, type `/globalchat add`!", color=discord.Color.red()))
                await message.add_reaction("⚠")
                gchannels.pop(str(message.channel.id))
                with open("json_files/globalchat.json", "w") as g:
                    json.dump(gchannels, g, indent=4)                
            except Exception:
                await message.channel.send(embed=discord.Embed(title="Error", description="Something went wrong while sending your message!", color=discord.Color.red()))
                await message.add_reaction("⚠")
            else:
                await message.delete()
                gchannels.pop(str(message.channel.id))
                for channel_id in list(gchannels.keys()):
                    try:
                        Webhook(gchannels[channel_id]).send(embed=embed, username=str(message.author), avatar_url=str(message.author.avatar_url))
                    except Exception:
                        gchannels.pop(channel_id)
                        with open("json_files/globalchat.json", "w") as g:
                            json.dump(gchannels, g, indent=4)     
                      

    @cog_ext.cog_subcommand(
        base="globalchat",
        name="add",
        description="Adds a channel to the global chat",
        options=[
            dict(
                name="channel",
                description="What channel do you want to add?",
                type=7,
                required="false",
            )
        ]
    )
    @commands.has_permissions(manage_channels=True)
    async def _globalchat_add(self, ctx, channel=None):
        if channel is None:
          channel = ctx.channel
        if isinstance(channel, discord.VoiceChannel):
          await ctx.send("Are you actually trying to add the global chat to a **voice channel?** :thinking:")
        elif isinstance(channel, discord.CategoryChannel):
          await ctx.send("Are you actually trying to add the global chat to a **category?** :thinking:")
        else:  
          await ctx.defer()
          webhook = await channel.create_webhook(name="Global Chat by TimMcBot")
          with open("json_files/globalchat.json", "r") as g:
              gchannels = json.load(g)
          gchannels[str(channel.id)] = webhook.url
          with open("json_files/globalchat.json", "w") as g:
              json.dump(gchannels, g, indent=4)
          embed = discord.Embed(
              title="Success!",
              description=f"The global chat has been initialized in {channel.mention}.",
              color=discord.Colour.green(),
          )
          embed.set_author(name="🌎 Channel added", icon_url=ctx.guild.icon_url)
          embed.add_field(name="Note:", value="Please remember to follow the rules when posting messages to the global chat.\n**Enter `/globalchat rules` to see them!**")
          await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="globalchat",
        name="rules",
        description="Shows the official rules for global chat posts"
    )
    async def _globalchat_rules(self, ctx):
        embed = discord.Embed(title="The official rules", description="**1)** Respect everyone and be nice to your fellow men.\n\n**2)** No NSFW content!\n\n**3)** No Spam!\n\n**4)** Be honest to other users. ||However, small pranks like [rickrolls](https://www.youtube.com/watch?v=DLzxrzFCyOs) are allowed ;)||", color=discord.Color.random())
        embed.add_field(name="Note:", value=f"If you violate the rules, you will be warned. When a user reaches too many warns, they will be banned from the global chat. {emojis['ban']}")
        embed.set_author(name="🌍 Global Chat", icon_url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

#setup

def setup(client):
    client.add_cog(globalchat(client))

