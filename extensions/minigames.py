import discord
from random import randint
from discord.ext import commands
from main import assets, emojis, get_prefix, is_not_private, get_client_color
import asyncio
from minigames import tictactoe, viergewinnt, chess, othello
import json

spiele = ["TicTacToe","Connect4","Chess","Othello"]
header_emojis = ["❌⭕","4️⃣","",""]
symbols = [["❌","⭕"],["🔴","🟡"],["",""],["*(Black)*","*(White)*"]]
react_emojis = [["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"],["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣"],["🇦","🇧","🇨","🇩","🇪","🇫","🇬","🇭","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣"],["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","0️⃣","<:a_:817909368765939722>","<:b_:817909368594235434>","<:c_:817909369026772993>","<:d_:817909368941969449>","<:e_:817909369316048926>","<:f_:817909368997281794>","<:g_:817909369186287666>","<:h_:817909369173704734>"]]
turncolors = [[14495300,14495300],[14495300,16632664],[15132648,3225405],[discord.Color.default(),15132648]]

#cogs

class minigames(commands.Cog):

  def __init__(self, client):
    self.client = client
    self.gtictactoe = {}
    self.gconnect4 = {}
  
  @commands.command(enabled=False, hidden=True, description="This command is not ready to use yet.", aliases=["schach"])
  @commands.cooldown(2, 10, commands.BucketType. user)
  async def chess(self, ctx, opponent : discord.Member):
    board,turn,won,spiel,channel = [0,0,0,0,0,0,0,0,0],0,0,2,[ctx.channel]
    accepted = await challenge(self, ctx.author, opponent, spiel, channel)
    if accepted:
      if randint(0,1) == 0: players = [ctx.author,opponent]
      else: players = [opponent,ctx.author]

      message = await create_emojis(channel, react_emojis[spiel], "The game is starting ...", players)
      content = chess.update(board)
      await create_card(players[0], players[1], spiel, content, turn, won, message, players)
      await ingame(self, channel,players,board,turn,spiel,message)


  @commands.command(enabled=False, hidden=True, description="Play othello against a server member!", aliases=["reversi"])
  @commands.cooldown(2, 10, commands.BucketType. user)
  async def othello(self, ctx, opponent : discord.Member):
    board,turn,won,spiel,channel = [0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,2,1,0,0,0, 0,0,0,1,2,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0],0,0,3,[ctx.channel]
    accepted = await challenge(self, ctx.author, opponent, spiel, channel)
    if accepted:
      if randint(0,1) == 0: players = [ctx.author,opponent]
      else: players = [opponent,ctx.author]

      message = await create_emojis(channel, react_emojis[spiel], "The game is starting ...", players)
      possible_moves,i = {},0
      for item in board:
        possible, possblties = othello.process_check_field(board, i, 1)
        if possible: possible_moves[i] = possblties
        i += 1
      content = othello.update(board, possible_moves)
      await create_card(players[0], players[1], spiel, content, turn, won, message, players, default_possible_moves=possible_moves)
      await ingame(self, channel,players,board,turn,spiel,message, default_possible_moves=possible_moves)

  @commands.Cog.listener()
  @othello.error
  async def othello_open(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      board,turn,won,spiel,channel = [0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,2,1,0,0,0, 0,0,0,1,2,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0],0,0,3,[ctx.channel]
      opponent, accepted = await open_game(self, ctx.author, spiel, ctx.channel)
      if accepted:
        if randint(0,1) == 0: players = [ctx.author,opponent]
        else: players = [opponent,ctx.author]

        message = await create_emojis(channel, react_emojis[spiel], f"{opponent.name} joined! The game is starting ...", players)
        possible_moves,i = {},0
        for item in board:
          possible, possblties = othello.process_check_field(board, i, 1)
          if possible: possible_moves[i] = possblties
          i += 1
        content = othello.update(board, possible_moves)
        await create_card(players[0], players[1], spiel, content, turn, won, message, players, default_possible_moves=possible_moves)
        await ingame(self, channel,players,board,turn,spiel,message, default_possible_moves=possible_moves)

  @commands.command(help="If you don't mention an opponent, an open game anyone can join will be started.", description="Play tictactoe against a server member!", aliases=["tic-tac-toe"])
  @commands.cooldown(2, 10, commands.BucketType. user)
  async def tictactoe(self, ctx, opponent : discord.Member):
    board,turn,won,spiel,channel = [0,0,0,0,0,0,0,0,0],0,0,0,[ctx.channel]
    accepted = await challenge(self, ctx.author, opponent, spiel, channel)
    if accepted:
      if randint(0,1) == 0: players = [ctx.author,opponent]
      else: players = [opponent,ctx.author]

      message = await create_emojis(channel, react_emojis[spiel], "The game is starting ...", players)
      content = tictactoe.update(board)
      await create_card(players[0], players[1], spiel, content, turn, won, message, players)
      await ingame(self, channel,players,board,turn,spiel,message)
  
  @commands.Cog.listener()
  @tictactoe.error
  async def tictactoe_open(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      board,turn,won,spiel,channel = [0,0,0,0,0,0,0,0,0],0,0,0,[ctx.channel]
      opponent, accepted = await open_game(self, ctx.author, spiel, ctx.channel)
      if accepted:
        if randint(0,1) == 0: players = [ctx.author,opponent]
        else: players = [opponent,ctx.author]

        message = await create_emojis(channel, react_emojis[spiel], f"{opponent.name} joined! The game is starting ...", players)
        content = tictactoe.update(board)
        await create_card(players[0], players[1], spiel, content, turn, won, message, players)
        await ingame(self, channel,players,board,turn,spiel,message)
  
  @commands.command(help="If you don't mention an opponent, an open game anyone can join will be started.", description="Play connect4 against a server member!", aliases=["connect-4","viergewinnt","4gewinnt"])
  @commands.cooldown(2, 10, commands.BucketType. user)
  async def connect4(self, ctx, opponent : discord.Member):
    board,turn,won,spiel,channel = [0,0,0,0,0,0,0, 0,0,0,0,0,0,0, 0,0,0,0,0,0,0, 0,0,0,0,0,0,0, 0,0,0,0,0,0,0, 0,0,0,0,0,0,0],0,0,1,[ctx.channel]
    accepted = await challenge(self, ctx.author, opponent, spiel, channel)
    if accepted:
      if randint(0,1) == 0: players = [ctx.author,opponent]
      else: players = [opponent,ctx.author]

      message = await create_emojis(channel, react_emojis[spiel], "The game is starting ...", players)
      content = viergewinnt.update(board)
      await create_card(players[0], players[1], spiel, content, turn, won, message, players)
      await ingame(self, channel,players,board,turn,spiel,message)
  
  @commands.Cog.listener()
  @connect4.error
  async def viergewinnt_open(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      board,turn,won,spiel,channel = [0,0,0,0,0,0,0, 0,0,0,0,0,0,0, 0,0,0,0,0,0,0, 0,0,0,0,0,0,0, 0,0,0,0,0,0,0, 0,0,0,0,0,0,0],0,0,1,[ctx.channel]
      opponent, accepted = await open_game(self, ctx.author, spiel, ctx.channel)
      if accepted:
        if randint(0,1) == 0: players = [ctx.author,opponent]
        else: players = [opponent,ctx.author]

        message = await create_emojis(channel, react_emojis[spiel], f"{opponent.name} joined! The game is starting ...", players)
        content = viergewinnt.update(board)
        await create_card(players[0], players[1], spiel, content, turn, won, message, players)
        await ingame(self, channel,players,board,turn,spiel,message)

  @commands.command(name="global-connect4", description="Starts a global Connect4 game.\nIf someone else runs the command, you'll be matched with them.", aliases=["gconnect4","globalconnect4","globalviergewinnt","global-viergewinnt","global4gewinnt","global-4gewinnt"])
  async def globalconnect4(self, ctx):
    author = ctx.author
    author : discord.User
    spiel = 1
    keys = list(self.gconnect4.keys())
    self.gconnect4, msg, channel, players, cont = await global_game(self, self.gconnect4, ctx, self.gconnect4, spiel, keys)
    if cont:
      board,turn,won = [0,0,0,0,0,0,0, 0,0,0,0,0,0,0, 0,0,0,0,0,0,0, 0,0,0,0,0,0,0, 0,0,0,0,0,0,0, 0,0,0,0,0,0,0],0,0
      content = viergewinnt.update(board)
      if len(channel) == 1:
        await create_card(players[0], players[1], spiel, content, turn, won, msg, players)
        await ingame(self, channel,players,board,turn,spiel,msg)
      else:
        try: self.gconnect4.pop(msg)
        except Exception: pass
        await create_card(players[0], players[1], spiel, content, turn, won, msg, players)
        await ingame(self, channel,players,board,turn,spiel,msg)
    elif not msg is None:
      await asyncio.sleep(2700)
      if msg in self.gconnect4:
        self.gconnect4.pop(msg)
        try: await msg.edit(content=ctx.author.mention, embed=discord.Embed(title="🌍 Timeout", description=f"{ctx.author.mention} started a global **{spiele[spiel]}** game, but nobody joined within 45 minutes. The game has been cancelled.", color=discord.Colour.blue()))
        except Exception: pass

  @commands.command(name="global-tictactoe", description="Starts a global TicTacToe game.\nIf someone else runs the command, you'll be matched with them.", aliases=["gtictactoe","globaltictactoe"])
  async def globaltictactoe(self, ctx):
    author = ctx.author
    author : discord.User
    spiel = 0
    keys = list(self.gtictactoe.keys())
    self.gtictactoe, msg, channel, players, cont = await global_game(self, self.gtictactoe, ctx, self.gtictactoe, spiel, keys)
    if cont:
      board,turn,won = [0,0,0,0,0,0,0,0,0],0,0
      content = tictactoe.update(board)
      if len(channel) == 1:
        await create_card(players[0], players[1], spiel, content, turn, won, msg, players)
        await ingame(self, channel,players,board,turn,spiel,msg)
      else:
        try: self.gtictactoe.pop(msg)
        except Exception: pass
        await create_card(players[0], players[1], spiel, content, turn, won, msg, players)
        await ingame(self, channel,players,board,turn,spiel,msg)
    elif not msg is None:
      await asyncio.sleep(2700)
      if msg in self.gtictactoe:
        self.gtictactoe.pop(msg)
        try: await msg.edit(content=ctx.author.mention, embed=discord.Embed(title="🌍 Timeout", description=f"{ctx.author.mention} started a global **{spiele[spiel]}** game, but nobody joined within 45 minutes. The game has been cancelled.", color=discord.Colour.blue())) 
        except Exception: pass
       

async def global_game(self, glist, ctx, ggl, spiel, keys):
  key = None
  for item in keys:
    if ggl[item] == ctx.author:
      await ctx.send(f"You already started another global {spiele[spiel]} game!")
      return ggl, None, None, None, False
    else: key = item
  if key is None:
    embed = discord.Embed(title="Waiting for another player ...", description="As soon as someone else runs the command, you'll be matched with them!", color= get_client_color(ctx))
    embed.set_author(name=f"🌍 Global {spiele[spiel]}", icon_url=ctx.author.avatar_url)
    embed.set_footer(text="🏓 You'll be notified when you have been matched.")
    msg = await ctx.send(None, embed=embed)
    ggl[msg] = ctx.author
    return ggl, msg, None, None, False
  else:
    channel,players = [ctx.channel, key.channel],[ctx.author, glist[key]]
    ggl.pop(key)
    await key.delete()
    if channel[0] == channel[1]:
      channel = [channel[0]]
      msg = await create_emojis(channel, react_emojis[spiel], "The game is starting ...", players)
    else:
      msg = await create_emojis(channel, react_emojis[spiel], "You have been matched with {}!", players)
    return ggl, msg, channel, players, True

async def open_game(self, author, spiel, channel):
  chal = discord.Embed(title=f"{author} started an open game!", description="React with 👍 if you want to join!", color=discord.Colour.green())
  chal.set_author(name=header_emojis[spiel]+" "+spiele[spiel], icon_url=author.avatar_url)
  message = await channel.send(None, embed=chal)
  await message.add_reaction("👍")

  def check(reaction, user):
    return reaction.message == message and str(reaction.emoji) == "👍"
  
  while True:
    try:
      reaction, user = await self.client.wait_for('reaction_add', timeout=180.0, check=check)
    except asyncio.TimeoutError:
      await message.clear_reactions()
      await message.edit(content=None, embed=discord.Embed(title=":alarm_clock: Timeout", description=f"{author.mention} started an open **{spiele[spiel]}** game, but noone joined in time.", color=discord.Colour.red()))
      return None, False
    else:
      if not (user.bot or user == author):
        await message.delete()
        return user, True
      elif user == author: await reaction.remove(user)      

async def challenge(self, author, opponent, spiel, channel):
  if author.id == opponent.id:
    await channel[0].send("Don't try to challenge yourself! :laughing:")
    return False
  elif opponent.bot:
    await channel[0].send(f"Bots can't play {spiele[spiel]}!")
    return False
  else:
    chal = discord.Embed(title=f"{author} challenged you!", description=f"Do you want to accept?", color=discord.Color.teal())
    chal.set_author(name=header_emojis[spiel]+" "+spiele[spiel], icon_url=author.avatar_url)
    message = await channel[0].send(f"{opponent.mention}", embed=chal)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    def check(reaction, user):
      return reaction.message == message and str(reaction.emoji) in ["✅","❌"] and user.id == opponent.id

    try:
      reaction, user = await self.client.wait_for('reaction_add', timeout=180.0, check=check)
    except asyncio.TimeoutError:
      await message.clear_reactions()
      await message.edit(content=None, embed=discord.Embed(title=":alarm_clock: Timeout", description=f"{author.mention} wanted  to play **{spiele[spiel]}** against {opponent.mention}, but {opponent.mention} didn't answer in time.", color=discord.Colour.red()))
    else:
      if str(reaction.emoji) == "✅":
        await message.delete()
        return True
      else:
        await message.clear_reactions()
        await message.edit(content=author.mention, embed=discord.Embed(title="Challenge denied", description=f"{opponent} denied {author}'s challenge.", color=discord.Colour.red()))
        return False

async def ingame(self,channel,players,default_board,default_turn,spiel,message,*,default_possible_moves=None):
  possible_moves = default_possible_moves
  won = 0
  step = 0
  board = default_board
  turn = default_turn
  def check(reaction, user):
    return reaction.message in message

  while True:
    try:
      reaction, user = await self.client.wait_for('reaction_add', timeout=180.0, check=check)
    except asyncio.TimeoutError:
      if turn == 0: other_user = players[1]
      else: other_user = players[0]
      card = message[0].embeds[0]
      card.set_field_at(len(card.fields)-1, name=f"⏰ {players[turn].name} didn't react in time", value=f"{other_user.mention} automatically wins", inline=False)
      for item in channel: await item.send(embed=discord.Embed(title=f"⏰ {players[turn].name} didn't react in time!", description=f"Therefore, {other_user.mention} automatically wins!", color=discord.Colour.random()))
      for item in message:
        await item.edit(content=None, embed=card)
        await item.clear_reactions()
      return
    else:
      if user.id == players[turn].id and str(reaction.emoji) in react_emojis[spiel]:
        field = react_emojis[spiel].index(str(reaction.emoji))
        await reaction.remove(user)      
        if spiel == 0:
          board, turn, won = tictactoe.process(board, turn+1, field)
          turn = turn -1 
          content = tictactoe.update(board)
          await create_card(players[0], players[1], spiel, content, turn, won, message, players)
        if spiel == 1:
          board, turn, won = viergewinnt.process(board, turn+1, field)
          turn = turn -1 
          content = viergewinnt.update(board)
          await create_card(players[0], players[1], spiel, content, turn, won, message, players, field)
        '''if spiel == 2:
          board, turn, won = chess.process(board, turn+1, field)
          turn = turn -1 
          content = chess.update(board)
          await create_card(players[0], players[1], spiel, content, turn, won, message, players)
        if spiel == 3:
          if step == 0 and field <= 7:
            highligh1 = field+1
            column = field
            content = othello.update(board)
            await create_card(players[0], players[1], spiel, content, turn, won, message, players, highligh1, step=step)
            step = 1
          elif step == 1 and field >= 8:
            highlight2 = field-8
            field = (field-8)*8+column
            board, turn, won = othello.process(board, turn+1, field)
            turn = turn -1 
            content = othello.update(board, highlight=highlight2)
            await create_card(players[0], players[1], spiel, content, turn, won, message, players, highligh1, step=step)
            step = 0'''
        if spiel == 3:
          board, turn, won, possible_moves = othello.process(board, turn+1, field, possible_moves)
          turn = turn -1 
          content = othello.update(board, possible_moves)
          await create_card(players[0], players[1], spiel, content, turn, won, message, players, field, default_possible_moves=possible_moves)
        if won != 0: return
      else: await reaction.remove(user)

async def create_emojis(channel, emojis, text, players):
  message,i = [],0
  if len(channel) == 1: message.append(await channel[0].send(f"{players[0].mention} {players[1].mention}", embed=discord.Embed(title=text, color=discord.Colour.random())))
  elif len(channel) == 2:
    message.append(await channel[0].send(f"{players[0].mention}", embed=discord.Embed(title=text.format(players[1]), color=discord.Colour.random())))
    message.append(await channel[1].send(f"{players[1].mention}", embed=discord.Embed(title=text.format(players[0]), color=discord.Colour.random())))
  for e in emojis:
    for item in message:
      await item.add_reaction(e)
  return message

async def create_card(p1, p2, spiel, content, turn, won, message, players, highlight=None, *, step=1, default_possible_moves=None):
  card = discord.Embed(title=spiele[spiel], color=turncolors[spiel][turn])
  az = ["❖","❖"]
  if spiel == 0:
    card.add_field(name="Board:", value=f"{content}{emojis['spacer']}")
    card.add_field(name="** **", value="** **")
  elif spiel == 1:
    if highlight is None:
      card.add_field(name="Board:", value=f"{emojis['spacer']}{content}\n{emojis['spacer']}")
    else:
      header = ""
      for i in range(7):
        if i == highlight: header = f"{header}🔽"
        else: header = f"{header}{emojis['spacer']}"
      card.add_field(name="Board:", value=f"{header}{content}\n{emojis['spacer']}")
  else: card.description=content
  if len(message) == 1:
    card.set_author(name="🏠 Local game", icon_url=message[0].guild.icon_url)
    card.add_field(name="Players:", value=f"{az[0]} **{str(p1)}** {symbols[spiel][0]}\n\n{az[1]} **{str(p2)}** {symbols[spiel][1]}\n{emojis['spacer']}", inline=True)
  elif len(message) == 2:
    card.set_author(name="🌍 Global game", icon_url=message[turn].guild.icon_url)
    card.add_field(name="Players:", value=f"{az[0]} **{str(p1)}** {symbols[spiel][0]}\n*Server: {message[0].guild}*\n\n{az[1]} **{str(p2)}** {symbols[spiel][1]}\nServer: *{message[1].guild}*\n{emojis['spacer']}", inline=True)
  if won != 0:
    if won == 3:
      card.add_field(name="➤ Tie!", value="** **", inline=False)
      for item in message: await item.clear_reactions(), await won_message(3, item.channel, None, len(message))     
    else:
      card.add_field(name=f"➤ {players[won-1].name} won!", value="** **", inline=False)
      gewinn = randint(14,25)
      for item in message: await item.clear_reactions(), await won_message(players[won-1], item.channel, gewinn, len(message))
  elif spiel == 0: card.add_field(name=f"➤ {players[turn].name}, it's your turn!", value="Please select an empty field.", inline=False)
  elif spiel == 1: card.add_field(name=f"➤ {players[turn].name}, it's your turn!", value="Please select a column.", inline=False)
  #elif spiel == 2: card.add_field(name=f"➤ {players[turn].name}, it's your turn!", value="Select the column of the paw you want to move.\n**(A - H)**\n\n\_ \_ - \_ \_", inline=False)
  elif spiel == 3:
    card.add_field(name=f"➤ {players[turn].name}, it's your turn!", value="Please select one of the marked fields.", inline=False)
    card.set_footer(text="Warning: Othello is still in beta testing.")
  for item in message:
    await item.edit(content=None, embed=card)

async def won_message(winner, channel, gewinn, servers):
  if winner == 3:
    embed=discord.Embed(title="Tie!", color=discord.Colour.random())
    if servers == 1: embed.description="**Nobody** gained XP."
    await channel.send(None, embed=embed)
  else:
    embed=discord.Embed(title=f"{winner} won! :tada:", color=discord.Colour.random())
    if servers == 1:
      with open("json_files/leveling.json", "r") as d:
        servers = json.load(d)

      xp = servers[str(channel.guild.id)][str(winner.id)]["xp"]
      servers[str(channel.guild.id)][str(winner.id)]["xp"] = xp + gewinn

      with open("json_files/leveling.json", "w") as d:
        json.dump(servers, d, indent=4)

      embed.title,embed.description,=f"You won, {winner.name}! :tada:",f"You gained **{gewinn} XP.**", 
      await channel.send(winner.mention, embed=embed)
    else: await channel.send(None, embed=embed)


#activate cogs

def setup(client):
  client.add_cog(minigames(client))