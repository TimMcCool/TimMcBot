import discord
import random
from random import randint
from discord.ext import commands, tasks
from main import assets, emojis, get_prefix, is_not_private, get_client_color
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from dhooks import Webhook
from PIL import Image, ImageFilter, ImageEnhance
import requests
import os
from datetime import datetime, timedelta
import json
import asyncio
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType

with open("json_files/rr.json", "r") as r:
    rr = json.load(r)

#functions

async def lock(self, ctx, channel, role):
    if channel is None:
        channel = ctx.channel
    if role is None:
        role = channel.guild.default_role
    
    if channel.overwrites_for(role).send_messages is False:
       await ctx.send(f"🔐 Channel already locked!")
       return
    overwrite = channel.overwrites_for(role)
    overwrite.send_messages = False
    await channel.set_permissions(role, overwrite=overwrite)

    await channel.set_permissions(ctx.guild.self_role, send_messages=True)
    if role == channel.guild.default_role:
        await ctx.send(f"🔒 Locked down **{channel.mention}**!")
    else:
        await ctx.send(f"🔒 Locked down **{channel.mention}** for **{role.name}**!")

async def unlock(self, ctx, channel, role):
    if channel is None:
        channel = ctx.channel
    if role is None:
        role = channel.guild.default_role

    if channel.overwrites_for(role).send_messages is None or channel.overwrites_for(role).send_messages is True:
       await ctx.send(f"🔓 Channel already unlocked!")
       return
    overwrite = channel.overwrites_for(role)
    overwrite.send_messages = None
    await channel.set_permissions(role, overwrite=overwrite)

    if role == channel.guild.default_role:
        await ctx.send(f"🔓 Unlocked **{channel.mention}**!")
    else:
        await ctx.send(f"🔓 Unlocked **{channel.mention}** for **{role.name}**!")

async def get_invites(self, ctx, user):
    embed = discord.Embed(
        title="Invites",
        description="This member hasn't created any invites yet!",
        color=get_client_color(ctx),
    )
    guild_invites = await ctx.guild.invites()
    invited_users = 0
    for invite in guild_invites:
        if invite.inviter.id == user.id:
            embed.description=""
            embed.add_field(
                name="discord.gg/" + invite.id,
                value=f"Created at: {invite.created_at.strftime('%m/%d/%Y')}\nChannel: {invite.channel.mention}\nUses: {invite.uses}\n",
            )
            invited_users += invite.uses
    embed.set_footer(text=f"Total invited users: {invited_users}")
    return embed

class utility(commands.Cog):
    def __init__(self, client):
        self.client = client

    #commands
    @commands.command()
    async def avatar(self, ctx, *, user: discord.User=None):
        if user is None:
            user = ctx.author
        embed = discord.Embed(title=f"{user}'s Avatar", url=str(user.avatar_url), color=get_client_color(ctx))
        embed.set_image(url=str(user.avatar_url))
        await ctx.send(embed=embed)


    @commands.command(brief="Gives you info on a specific invite link", aliases=["inspect_invite"])
    async def inspect(self, ctx, invite_link):
        try:
            invite = await self.client.fetch_invite(invite_link, with_counts=True)
            if invite.guild.id == ctx.guild.id:
                guild_invites = await ctx.guild.invites()
                invite = discord.utils.get(guild_invites, code = invite.code)

                embed = discord.Embed(title="discord.gg/"+invite.code, color=get_client_color(ctx))
                embed.set_author(name="🔗 Invite link information", icon_url=ctx.guild.icon_url)
                embed.add_field(name="Created by:", value=f"```{invite.inviter}```")
                embed.add_field(name="Uses:", value=f"```{invite.uses}```")
                if invite.max_uses == 0:
                    embed.add_field(name="Max. uses:", value=f"```No limit```")
                else:
                    embed.add_field(name="Max. uses:", value=f"```{invite.max_uses}```")
                embed.add_field(name="Channel:", value=invite.channel.mention)
                embed.add_field(name="Created at:", value=f"```{invite.created_at.strftime('%m/%d/%Y')}```")
                if invite.max_age == 0:
                    embed.add_field(name="Expires at:", value=f"```Won't expire```")
                else:
                    expiredate = invite.created_at + timedelta(seconds=invite.max_age)
                    embed.add_field(name="Expires at:", value=f"```{expiredate.strftime('%m/%d/%Y')}```")
                embed.add_field(name="Temporary membership allowed?", value=f"{invite.temporary}", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("This invite belongs to another server! 🧭")
        except Exception:
            await ctx.send("This invite link wasn't found! 👀")


    @commands.command()
    async def servericon(self, ctx):
        try:
            await ctx.send(str(ctx.guild.icon_url))
        except Exception:
            await ctx.send("This server has no icon :confused:")


    @commands.command(description="Revokes an invite link")
    @commands.has_permissions(manage_guild=True)
    async def revoke(self, ctx, invite_link, *, reason=None):
        try:
            invite = await self.client.fetch_invite(invite_link, with_counts=True)
        except Exception:
            await ctx.send("This invite link wasn't found! 👀")   
        else:
            if invite.guild.id == ctx.guild.id:
                if reason is None:
                    reason = f"Revoked by {ctx.author}"
                await invite.delete(reason=reason)
                if reason == f"Revoked by {ctx.author}":
                    reason = "No reason provided"
                embed=discord.Embed(title=f"discord.gg/{invite.code}", color=get_client_color(ctx))
                embed.add_field(name="Revoked by:", value=""+str(ctx.author)+"", inline=False)
                embed.add_field(name="Reason:", value=""+reason+"", inline=False)
                embed.set_author(name="Invite revoked", icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)             
            else:
                await ctx.send("This invite belongs to another server! 🧭")     

    @cog_ext.cog_slash(
        name="lock",
        description="Locks a channel",
        options = [
            dict(
                name = "channel",
                description = "the channel to lock",
                type = 7,
                required = "false"
            ),
            dict(
                name = "role",
                description = "the role you want to lock the channel for",
                type = 7,
                required = "false"
            )
        ]
    )
    @commands.has_permissions(manage_channels=True)
    async def _lock(self, ctx, channel: discord.TextChannel=None, role: discord.Role=None):
        await lock(self, ctx, channel, role)

    @commands.command(description="Denies the **`Send messages`** permission for **`@everyone`** or a specific role.\nDepending on the permission settings of the channel, some members still may be able to send messages.")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel=None, *, role: discord.Role=None):
        await lock(self, ctx, channel, role)

    @commands.command(description="Locks down all channels of a category for @everyone")
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx, *, category: discord.CategoryChannel):
        role = ctx.guild.default_role
    
        for channel in category.text_channels:
            overwrite = channel.overwrites_for(role)
            overwrite.send_messages = False
            await channel.set_permissions(role, overwrite=overwrite)

        await ctx.channel.set_permissions(ctx.guild.self_role, send_messages=True)
        await ctx.send(f"🔒 Locked down the category **{category.mention}**!")

    @cog_ext.cog_slash(
        name="unlock",
        description="Unlocks a channel",
        options = [
            dict(
                name = "channel",
                description = "the channel to unlock",
                type = 7,
                required = "false"
            ),
            dict(
                name = "role",
                description = "the role you want to lock the channel for",
                type = 7,
                required = "false"
            )
        ]
    )
    @commands.has_permissions(manage_channels=True)
    async def _unlock(self, ctx, channel: discord.TextChannel=None, role: discord.Role=None):
        await unlock(self, ctx, channel, role)


    @commands.command(brief="Unlocks a channel for @everyone or a specific role", description="Gives **`@everyone`** or a specific role the **`Send messages`** permission.\nDepending on the permission settings of the channel, some members still may not be able to send messages.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel=None, *, role: discord.Role=None):
        await unlock(self, ctx, channel, role)

    @cog_ext.cog_slash(
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
    async def _invites(self, ctx, user=None):
        if user is None:
            user = ctx.author
        embed = await get_invites(self, ctx, user)
        embed.set_author(name="📨 " + str(user), icon_url=user.avatar_url)
        await ctx.send(embed=embed)


    @commands.command(brief="Shows the invites a user created")
    async def invites(self, ctx, *, user: discord.User=None):
        if user is None:
            user = ctx.author
        embed = await get_invites(self, ctx, user)
        embed.set_author(name="📨 " + str(user), icon_url=user.avatar_url)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="id",
        description="Gives you the id of something",
        options=[
            dict(
                name="member",
                description="Gives you the user id",
                type=6,
                required="false",
            ),
            dict(
                name="role",
                description="Gives you the role id",
                type=8,
                required="false",
            ),
            dict(
                name="channel_or_category",
                description="Gives you the channel or category id",
                type=7,
                required="false",
            )
        ]) 
    async def _id(self, ctx, member: discord.Member= None, role: discord.Role= None, channel_or_category=None):
        channel = channel_or_category
        if not member is None:
            await ctx.send(
                f"The user id of **{member}** is `{member.id}` 🆔"
            )
        if not role is None:
            await ctx.send(
                f"The role id of **{role}** is `{role.id}` 🆔"
            )
        if not channel is None:
            await ctx.send(
                f"The id of **{channel.mention}** is `{channel.id}` 🆔"
            )
        if role is None and member is None and channel is None:
            await ctx.send(
                f"Your user id is `{ctx.author.id}` 🆔"
            )


    @commands.command(brief="Gives you the id of a user")
    async def id(self, ctx, *, user: discord.User=None):
        if user is None:
            await ctx.send(
                f"Your user id is `{ctx.author.id}` 🆔"
            )
        else:
            await ctx.send(f"The user id of **{user}** is `{user.id}` 🆔")

    @cog_ext.cog_slash(
        name="embed",
        description="Allows you to send embeds!",
        options = [
            dict(
                name = "title",
                description = "The title of the embed",
                type = 3,
                required = "false"
            ),
            dict(
                name = "description",
                description = "The description of the embed",
                type = 3,
                required = "false"
            ),
            dict(
                name = "color",
                description = "The color of the embed",
                type = 3,
                required = "false",
                choices = [
                    create_choice(name="random", value="8"),
                    create_choice(name="default", value="9"),
                    create_choice(name="blue", value="0"),
                    create_choice(name="dark blue", value="1"),
                    create_choice(name="green", value="2"),
                    create_choice(name="dark green", value="3"),
                    create_choice(name="gold", value="4"),
                    create_choice(name="brown", value="5"),
                    create_choice(name="magenta", value="6"),
                    create_choice(name="dark magenta", value="7"),

                    create_choice(name="red", value="10"),
                    create_choice(name="teal", value="11"),
                    create_choice(name="purple", value="12"),
                    create_choice(name="dark grey", value="13"),
                    create_choice(name="dark red", value="14"),
                    create_choice(name="greyish purple", value="15"),
                    create_choice(name="orange", value="16"),
                    create_choice(name="dark orange", value="17"),
                    create_choice(name="dark teal", value="18"),
                    create_choice(name="blueish purple", value="19")
                ]
            ),
            dict(
                name = "footer",
                description="shown at the bottom",
                type = 3,
                required = "false"
            ),
            dict(
                name = "footer_icon_url",
                description = "shown at the bottom",
                type = 3,
                required = "false"
            ),
            dict(
                name = "author",
                description = "shown on the top",
                type = 3,
                required = "false"
            ),
            dict(
                name = "author_icon_url",
                description = "shown on the top",
                type = 3,
                required = "false"
            ),
            dict(
                name = "thumbnail_url",
                description = "small at the top right",
                type = 3,
                required = "false"
            ),
            dict(
                name = "image_url",
                description = "big at the bottom",
                type = 3,
                required = "false"
            )

        ]
    )
    @commands.check(is_not_private)
    @commands.has_permissions(embed_links=True)
    async def _embed(self, ctx, title=None, description="** **", color=None, footer=None, footer_icon_url=None, author=None, author_icon_url=None, thumbnail_url=None, image_url=None):
        await ctx.defer(hidden=True)
        colors = [
            discord.Color.blue(),
            discord.Color.dark_blue(),
            discord.Color.green(),
            discord.Color.dark_green(),
            discord.Color.gold(),
            discord.Color.dark_gold(),
            discord.Color.magenta(),
            discord.Color.dark_magenta(),
            discord.Color.random(),
            discord.Color.default(),

            discord.Color.red(),
            discord.Color.teal(),
            discord.Color.purple(),
            discord.Color.dark_gray(),
            discord.Color.dark_red(),
            discord.Color.greyple(),
            discord.Color.orange(),
            discord.Color.dark_orange(),
            discord.Color.dark_teal(),
            discord.Color.blurple()    

        ]
        embed = discord.Embed(description=description)
        if not title is None:
            embed.title = title
        if not color is None:
            embed.color = colors[int(color)]
        if not footer is None:
            if footer_icon_url is None:
                embed.set_footer(text=footer)
            else:
                embed.set_footer(text=footer, icon_url=footer_icon_url)
        if not author is None:
            if author_icon_url is None:
                embed.set_author(name=author)
            else:
                embed.set_author(name=author, icon_url=author_icon_url)
        if not thumbnail_url is None:
            embed.set_thumbnail(url=thumbnail_url)
        if not image_url is None:
            embed.set_image(url=image_url)
    
        webhook = await ctx.channel.create_webhook(name="Temporary webhook by TimMcBot")
        await webhook.send(embed=embed, username=ctx.author.display_name, avatar_url=ctx.author.avatar_url)
        await webhook.delete()
        await ctx.send(f":ok_hand: Your embed was sent successfully!", hidden=True)

    @commands.command(aliases=["rr","reactionroles"], brief="Creates a reaction role. Everyone will be able to pick up the role", usage="**Example:**\n```{}reactionrole 🎮 @Gamers```would allow members to pick the @Gamers role by reacting with :video_game:\n", description="Creates a reaction role. Members will be able to get the role by reacting to a message TimMcBot sends.\nBeware that everyone will be able to pick up the role.")
    @commands.has_permissions(manage_guild=True, manage_roles=True)
    async def reactionrole(self, ctx, emoji : str, *, role : discord.Role):#, emoji2 :str=None, role2 :discord.Role=None, emoji3 :str=None, role3 :discord.Role=None):
        global rr
        if role.position > ctx.guild.get_member(self.client.user.id).top_role.position:
            embed=discord.Embed(title="Error", description="You can only choose roles that are below my highest role.", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        if ctx.author.top_role.position > role.position:
            perms = role.permissions
            if perms.administrator is True or perms.manage_channels is True or perms.manage_guild is True or perms.manage_messages is True or perms.manage_nicknames is True or perms.ban_members is True or perms.kick_members is True:
                embed=discord.Embed(title="Warning", description="This role has dangerous permissions!", color=discord.Color.gold())
                embed.set_footer(text="Do you still want to allow everyone to pick it?")
                reminder = await ctx.send(embed=embed)
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
                    await reminder.clear_reactions()
                    await reminder.edit(
                        content=None,
                        embed=discord.Embed(
                            title=":alarm_clock: Timeout", color=discord.Colour.red()
                        ),
                    )
                    return
                else:
                    if str(reaction.emoji) == "❌":
                        await ctx.send("👌 ok, the reaction role won't be created then.")
                        return

            embed=discord.Embed(title="Reaction role", description=f"{emoji} • {role.mention}", color=discord.Color.random())
            embed.set_footer(text="React to get the role!")
            message = await ctx.send(embed=discord.Embed(title="Loading"))
            try:
                await message.add_reaction(emoji)
            except discord.errors.HTTPException:
                await message.edit(content="You didn't enter a valid emoji!")
            else:
                await message.edit(content="", embed=embed)
                if not str(ctx.guild.id) in rr:
                    rr[str(ctx.guild.id)] = {}
                rr[str(ctx.guild.id)][str(message.id)] = {emoji : role.id}
                with open("json_files/rr.json", "w") as r:
                    json.dump(rr, r, indent=4)

        else:
            embed=discord.Embed(title="Error", description="You can only choose roles that are lower than your highest role!", color=discord.Color.red())
            embed.add_field(name=f"Position of @{role.name}", value=f"```{role.position}```")
            embed.add_field(name="Position of your highest role", value=f"```{ctx.author.top_role.position}```")
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.guild_id) in rr:
            if str(payload.message_id) in rr[str(payload.guild_id)]:
                data = rr[str(payload.guild_id)][str(payload.message_id)]
                if str(payload.emoji) in data:
                    guild = await self.client.fetch_guild(payload.guild_id)
                    role = guild.get_role(data[str(payload.emoji)])
                    await payload.member.add_roles(role, reason=f"Reaction role")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if str(payload.guild_id) in rr:
            if str(payload.message_id) in rr[str(payload.guild_id)]:
                data = rr[str(payload.guild_id)][str(payload.message_id)]
                if str(payload.emoji) in data:
                    guild = await self.client.fetch_guild(payload.guild_id)
                    role = guild.get_role(data[str(payload.emoji)])
                    member = await guild.fetch_member(payload.user_id)
                    await member.remove_roles(role, reason=f"Reaction role")

# activate cogs


def setup(client):
    client.add_cog(utility(client))