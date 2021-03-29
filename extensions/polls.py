import discord
import random
from random import randint
from discord.ext import commands, tasks
from main import assets, emojis, get_prefix, is_not_private, get_client_color
import json
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

#cogs

def get_poll_answer_options():
  options = [
    dict(
      name = "question",
      description =  "Question",
      type =  3,
      required =  "true"),
    dict( 
    name = "type",
    description =  "'normal' is recommended",
    type =  3,
    required =  "true",
    choices=[
          create_choice(
          name="normal",
          value="0"
        ),
          create_choice(
          name="anonymous",
          value="1"
        ),
          create_choice(
          name="strict",
          value="2"
        ),
          create_choice(
          name="anonymous and strict",
          value="3"
        )
      ]
    )]
  '''
  dict( 
  name = "anonymous",
  description =  "Do you want your poll to be anonymous?",
  type =  5,
  required =  "true"),
  dict(
  name = "strict",
  description =  "Do you want your poll to be strict so users can only vote once?",
  type =  5,
  required =  "true"),
  dict(
  name = "question",
  description =  "Question",
  type =  3,
  required =  "true")]
  '''
  alphabet = "abcdefghijklmnopqrst"
  for i in range(0,20):
    options.append(dict(
      name = f"choice_{alphabet[i]}",
      description =  f"Answer option {alphabet[i]}",
      type =  3,
      required = "false"))
  return options

class polls(commands.Cog):

  def __init__(self, client):
    self.client = client

    #commands

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload):
    with open("json_files/polls.json", "r") as p:
      running_polls = json.load(p)
    if str(payload.guild_id) in running_polls:
      if str(payload.message_id) in running_polls[str(payload.guild_id)]:
        if running_polls[str(payload.guild_id)][str(payload.message_id)]["ended"] is True:
          channel = await self.client.fetch_channel(payload.channel_id)
          message = await channel.fetch_message(payload.message_id)
          reactions = message.reactions
          for reaction in reactions:      
            if not str(reaction.emoji) == str(payload.emoji): continue
            users = list(await reaction.users().flatten())
            for user in users:
              if user.bot: continue
              if user.id == payload.user_id:
                await reaction.remove(user)
                return
        elif str(payload.emoji) == "❎" and payload.user_id == running_polls[str(payload.guild_id)][str(payload.message_id)]['author']:
          data = running_polls[str(payload.guild_id)]
          channel = await self.client.fetch_channel(payload.channel_id)
          message = await channel.fetch_message(payload.message_id)          
          embed = (message.embeds)[0]

          embed.set_footer(text = "This poll has been stopped.\nNew votes will automatically be removed.")
          data[str(payload.message_id)]['ended'] = True

          await message.edit(embed=embed)

          running_polls[str(payload.guild_id)] = data
          with open("json_files/polls.json", "w") as p:
            json.dump(running_polls, p, indent=4)

        elif running_polls[str(payload.guild_id)][str(payload.message_id)]["strict"] is True:
          channel = await self.client.fetch_channel(payload.channel_id)
          message = await channel.fetch_message(payload.message_id)
          reactions = message.reactions
          for reaction in reactions:      
            if str(reaction.emoji) == str(payload.emoji): continue
            users = list(await reaction.users().flatten())
            for user in users:
              if user.bot: continue
              if user.id == payload.user_id:
                await reaction.remove(user)
                return
  
  @cog_ext.cog_slash(name="poll", description="Start a poll (up to 20 choices)", options = get_poll_answer_options())
  @commands.check(is_not_private)
  async def _poll_create(self, ctx, question, * data):
    await ctx.defer(hidden=True)
    data = list(data)
    _type = int(data[0])
    data[0] = question
    anonymous = False
    strict = False
    if _type == 1 or _type == 3:
      anonymous = True
    if _type == 2 or _type == 3:
      strict = True
    await poll_create(self, ctx, data, anonymous, strict, slash=True)


  @cog_ext.cog_subcommand(base="polls", name="results", description="Shows the results of a poll",
    options = [
      dict( 
      name = "poll_message_id",
      description =  "The message id of the poll. If you leave it empty, it will show the latest poll.",
      type =  3,
      required =  "false")
      ]
    )
  @commands.check(is_not_private)
  async def _poll_results(self, ctx, poll_message_id=None):
    await poll_results(self, ctx, poll_message_id, slash=True)

  @commands.command(help="If you have permission to use slash commands, you can also use `/poll` to create polls!", description='Creates a normal poll.', usage='**Yes/No polls:**\n```{0}poll "Do you like the color blue?"```\n**Multiple answer options (up to 20):**\n```{0}poll "What is your favorite color?" "Blue" "Green" "Yellow"```')
  @commands.cooldown(3, 15, commands.BucketType.user)
  async def poll(self, ctx, * data):
    await ctx.message.delete()
    await poll_create(self, ctx, data, False, False)

  @commands.command(help="If you have permission to use slash commands, you can also use `/poll` to create polls!", description="Creates an anonymous poll that doesn't show the author's name.", usage='**Yes/No polls:**\n```{0}anonymouspoll "Do you like anonymous polls?"```\n**Multiple answer options (up to 20):**\n```{0}anonymouspoll "What is your least favorite color?" "Blue" "Green" "Yellow"```')
  @commands.cooldown(3, 15, commands.BucketType.user)
  async def anonymouspoll(self, ctx, * data):
    await ctx.message.delete()
    await poll_create(self, ctx, data, True, False)

  @commands.command(help="If you have permission to use slash commands, you can also use `/poll` to create polls!", description="Creates a poll, but members won't be able to vote for multiple answer options.", usage='**Yes/No polls:**\n```{0}strictpoll "Do you like strict polls?"```\n**Multiple answer options (up to 20):**\n```{0}strictpoll "What color do you like most?" "Blue" "Green" "Yellow"```')
  @commands.cooldown(3, 15, commands.BucketType.user)
  async def strictpoll(self, ctx, * data):
    await ctx.message.delete()
    await poll_create(self, ctx, data, False, True)

  @commands.command(description="Shows all running and all stopped polls on the server.", aliases=["polls","allpolls","serverpolls"])
  async def pollslist(self, ctx):
    with open("json_files/polls.json", "r") as p:
      running_polls = json.load(p)
    embed = discord.Embed(title="Polls", description="", color=discord.Color.random())
    if str(ctx.guild.id) in running_polls:
      embed.set_footer(text="Click on a poll to jump directly to it!")
      data = running_polls[str(ctx.guild.id)]
      running = ""
      stopped = ""
      for poll in data:
        if data[poll]['ended'] is False:
          running += f"[❖ {data[poll]['name']}]({data[poll]['url']})\n"
        else:
          stopped += f"[◈ {data[poll]['name']}]({data[poll]['url']})\n"
      if not running == "": embed.description = f"**Running polls:**\n{running}\n"
      if not stopped == "": embed.description += f"**Stopped polls:\n**{stopped}"
    else: embed.description = "No polls have been created on this server yet!"
    embed.set_thumbnail(url=ctx.guild.icon_url)
    embed.set_author(name="📊 "+ctx.guild.name)
    await ctx.send(embed=embed)

  @commands.command(help="You can also stop your polls by reacting with ❎!", name="stop-poll", description="Allows you to stop one of your polls. New votes on stopped polls will automatically be removed.", aliases=["stoppoll","end-poll","endpoll"])
  async def stoppoll(self, ctx, poll_message_id):
    with open("json_files/polls.json", "r") as p:
      running_polls = json.load(p)
    if str(ctx.guild.id) in running_polls:
      data = running_polls[str(ctx.guild.id)]
      if poll_message_id in data:
        if data[poll_message_id]['author'] == ctx.author.id:
          try: message = await ctx.channel.fetch_message(poll_message_id)
          except Exception: await ctx.send("Please go to the **channel** where you created the poll and run the command again!")
          else:
            embed = (message.embeds)[0]

            embed.set_footer(text = "This poll has been stopped.\nNew votes will automatically be removed.")
            data[poll_message_id]['ended'] = True

            await message.edit(embed=embed)

            embed = discord.Embed(description=f"[Click here to jump to it.]({data[poll_message_id]['url']})", color=discord.Color.random())
            embed.set_author(name="📊 Poll stopped", icon_url=ctx.author.avatar_url)
            await ctx.message.add_reaction(emojis['checkmark'])
            await ctx.send(embed=embed)
            running_polls[str(ctx.guild.id)] = data
            with open("json_files/polls.json", "w") as p:
              json.dump(running_polls, p, indent=4)

        else: await ctx.send("That poll was **created by someone else!** You can't stop other's polls.")
      else: await ctx.send("Couldn't find your poll! Please make sure you entered the **correct message id.**")
    else: await ctx.send("Couldn't find your poll! Please make sure you're on the **server** where you created the poll.")

  @commands.command(description="Shows the results of a poll.\nIf no message id is provided, it shows the result of the latest poll on the server.", aliases=["poll-results","result","poll-result"])
  async def results(self, ctx, *, poll_message_id=None):
    await poll_results(self, ctx, poll_message_id)

async def poll_results(self, ctx, poll_message_id=None, slash=False):
  with open("json_files/polls.json", "r") as p:
    running_polls = json.load(p)
  if str(ctx.guild.id) in running_polls:
    data = running_polls[str(ctx.guild.id)]
    if poll_message_id is None:
      keys = list(data.keys())
      keys.reverse()
      poll_message_id = keys[0]
    if poll_message_id in data:
      channel = await self.client.fetch_channel(data[poll_message_id]['channel'])
      message = await channel.fetch_message(int(poll_message_id))

      embed=discord.Embed(title=data[poll_message_id]['name'], description=f"[Click here]({data[poll_message_id]['url']}) to jump to the poll!", color=discord.Color.random(), timestamp=message.created_at)

      options = data[poll_message_id]['options']
      result = {}
      i = 0
      total_reacts = 0
      for reaction in message.reactions:
        if str(reaction.emoji) == "❎":
          continue
        total_reacts += reaction.count - 1
      if total_reacts <= 0:
        embed.set_author(name="📊 Poll results")
        embed.description = f"There are no results to show because noone has voted yet!"
        await ctx.send(embed=embed)
        return

      for tp in zip(message.reactions, options):
        result[tp[1]] = tp[0].count-1
        percentage = round(((tp[0].count-1) / total_reacts) * 100)

        bar = ""
        for i in range(20):
          if round((i+1)*5) <= percentage:
            bar += "█"
          else:
            bar += "░"
        
        votes = tp[0].count-1
        if votes == 1:
          embed.add_field(name=f"{tp[1]}", value=f"{bar} {percentage}% **({votes} vote)**", inline=False)
        elif votes == 0:
          embed.add_field(name=f"{tp[1]}", value=f"{bar} {percentage}% ({votes} votes)", inline=False)  
        else:
          embed.add_field(name=f"{tp[1]}", value=f"{bar} {percentage}% **({votes} votes)**", inline=False)  
        i +=1
      embed.set_author(name="📊 Poll results")
      embed.set_footer(text=f"{total_reacts} total votes | Poll created at")

      await ctx.send(embed=embed)
    
    else:
      if slash is True:
        await ctx.send("This poll wasn't found!", hidden=True)
      else:
        await ctx.send("This poll wasn't found!")
  else:
    if slash is True:
      await ctx.send("No polls found on this server!", hidden=True)
    else:
      await ctx.send("No polls found on this server!")


async def poll_create(self, ctx, data, anonymous, strict, *, slash=False):
  options = list(data)
  if not len(options) == 0: question = options.pop(0)
  else:
    await ctx.send("Please specify a poll!")
    return

  if len(options) > 20: options = options[:20]
  if len(options) == 0:
    embed=discord.Embed(title=question, color=discord.Color.random())
    if strict is True:
      embed.set_footer(text="This is a strict poll, you can only vote for one answer option.")
    if anonymous:
      embed.set_author(name="📊 Anonymous Poll")
    else:
      embed.set_author(name=f"📊 Poll by {ctx.author}", icon_url=ctx.author.avatar_url)
    poll = await ctx.channel.send(embed=embed)
    
    await poll.add_reaction("👍")
    await poll.add_reaction("👎")

    options = ["Upvotes","Downvotes"]
  else:
    content, i, reactions = "", 0, []
    alphabet = "🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹🇺🇻🇼🇽🇾🇿"
    for item in options:
      reactions.append(f"{alphabet[i]}")
      content, i = f"{content}{alphabet[i]} {item}\n\n", i + 1
    embed = discord.Embed(title=question, description=content, color=discord.Color.random())
    if strict is True:
      embed.set_footer(text="This is a strict poll, you can only vote for one answer option.")
    if anonymous:
      embed.set_author(name="📊 Anonymous Poll")
    else:
      embed.set_author(name=f"📊 Poll by {ctx.author}", icon_url=ctx.author.avatar_url)
    poll = await ctx.channel.send(embed=embed)
    for reaction in reactions:
      await poll.add_reaction(reaction)
  with open("json_files/polls.json", "r") as p:
    running_polls = json.load(p)
  if str(ctx.guild.id) in running_polls: data = running_polls[str(ctx.guild.id)]
  else: data = {}
  data[str(poll.id)] = dict(name = question, strict = strict, url = poll.jump_url, author = ctx.author.id, ended = False, channel = ctx.channel.id, options = options)
  running_polls[str(ctx.guild.id)] = data
  with open("json_files/polls.json", "w") as p:
    json.dump(running_polls, p, indent=4)
  await poll.add_reaction("❎")
  if slash is True:
    await ctx.send("Your **poll** has been **created!** You can stop it anytime by reacting with ❎", hidden=True)
  else:
    await ctx.send("The **poll** has been **created!** The poll author can stop it anytime by reacting with ❎", delete_after=15.0)

#activate cogs


def setup(client):
    client.add_cog(polls(client))
