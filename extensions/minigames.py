import discord
from random import randint, choice
from discord.ext import commands
from main import assets, emojis, get_prefix, is_not_private, get_client_color
import asyncio
from minigames import tictactoe, viergewinnt, chess, othello
import json
import os
from PIL import Image, ImageFilter, ImageEnhance
from math import floor

spiele = ["TicTacToe", "Connect4", "Chess", "Othello"]
header_emojis = ["❌⭕", "4️⃣", "", ""]
symbols = [["❌", "⭕"], ["🔴", "🟡"], ["", ""], ["*(Black)*", "*(White)*"]]
react_emojis = [
    ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"],
    ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"],
    [
        "🇦",
        "🇧",
        "🇨",
        "🇩",
        "🇪",
        "🇫",
        "🇬",
        "🇭",
        "1️⃣",
        "2️⃣",
        "3️⃣",
        "4️⃣",
        "5️⃣",
        "6️⃣",
        "7️⃣",
        "8️⃣",
    ],
    [
        "1️⃣",
        "2️⃣",
        "3️⃣",
        "4️⃣",
        "5️⃣",
        "6️⃣",
        "7️⃣",
        "8️⃣",
        "9️⃣",
        "0️⃣",
        "<:a_:817909368765939722>",
        "<:b_:817909368594235434>",
        "<:c_:817909369026772993>",
        "<:d_:817909368941969449>",
        "<:e_:817909369316048926>",
        "<:f_:817909368997281794>",
        "<:g_:817909369186287666>",
        "<:h_:817909369173704734>",
    ],
]
turncolors = [
    [14495300, 14495300],
    [14495300, 16632664],
    [15132648, 3225405],
    [discord.Color.default(), 15132648],
]

# cogs


class minigames(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.gtictactoe = {}
        self.gconnect4 = {}

    @commands.command(name="2048", usage=":bulb: **How to play:**\nUse your arrow keys to move the tiles. When two tiles with the same number touch, they merge into one! Can you get the 2048 tile?\nIf you can't move the tiles anymore and can't merge two tiles into one, your game is over.\n")
    @commands.cooldown(1, 19, commands.BucketType.user)
    async def twothousendtwentyfour(self, ctx):
        with open("json_files/2048highscores.json", "r") as h:
            highscores = json.load(h)

        if not str(ctx.author.id) in highscores:
            highscores[str(ctx.author.id)] = 0
            with open("json_files/2048highscores.json", "w") as h:
                json.dump(highscores, h, indent=4)

        highscore = highscores[str(ctx.author.id)]

        color = get_client_color(ctx)

        embed = discord.Embed(title="New 2048 game", description="Do you want to see the **board as picture?**", color=color)
        embed.set_footer(text="This looks better, but can slow down gameplay")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/817155267816587326/828309605947539476/2048_1.png")
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        message = await ctx.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")

        def check(reaction, user):
            return (
                reaction.message.id == message.id
                and user.id == ctx.author.id
                and str(reaction.emoji) in ["👎","👍"]
            )

        reaction, user = await self.client.wait_for(
            "reaction_add", check=check
        )

        if str(reaction.emoji) == "👎":
            badinternet = True
        else:
            badinternet = False
        
        await message.delete()

        arrows = ["◀","🔼","🔽","▶"]
        score = 0
        board = [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]
        zug_nr = 0
        change = None
        changed = True
        win = False
        game_over = False

        def graphic():
            img = Image.open('assets/2048/board.png')
            i=0
            for field in board:
                if not field == 0:
                    field_img = Image.open(f'assets/2048/{field}.png')
                    field_img = field_img.resize((138,138))
                    img.paste(field_img, (i%4*151+17, floor(i/4) * 151+17))
                
                i+=1

            id = randint(0,9999999999)
            img = img.resize((260,260))
            img.save(f'temp_files/2048-{id}.png', optimize = True, compress_level = 20)
            return id

        def spawn_random():
            #get items that are 0
            empty = []
            i = 0
            for field in board:
                if field == 0:
                    empty.append(i)
                i += 1
            
            #spawn random item
            if not len(empty) == 0:
                if randint(0,3) == 0:
                    board[choice(empty)] = 4
                else:
                    board[choice(empty)] = 2
            return

        def process(arrow :int, old_score):
            
            score = old_score
            change = 0
            changed = False
            if arrow == 0: #left
                for iter in range(0,3):
                    for i in range(15,0,-1):
                        if not i % 4 == 0 or board[i] == 0:
                            if board[i-1] == 0:
                                board[i-1] = board[i]
                                board[i] = 0
                                changed = True
                for i in range(0,15,1):
                    if not i % 4 == 0 or board[i] == 0:
                        if board[i-1] == board[i]:
                            change += board[i]*2
                            board[i-1] = board[i]*2
                            board[i] = 0
                for iter in range(0,3):
                    for i in range(15,0,-1):
                        if not i % 4 == 0 or board[i] == 0:
                            if board[i-1] == 0:
                                board[i-1] = board[i]
                                board[i] = 0
                                changed = True

            if arrow == 1: #up
                for iter in range(0,3):
                    for i in range(15,3,-1):
                        if not board[i] == 0:
                            if board[i-4] == 0:
                                board[i-4] = board[i]
                                board[i] = 0
                                changed = True
                for i in range(3,15,1):
                    if not board[i] == 0:
                        if board[i-4] == board[i]:
                            change += board[i]*2
                            board[i-4] = board[i]*2
                            board[i] = 0
                for iter in range(0,3):
                    for i in range(15,3,-1):
                        if not board[i] == 0:
                            if board[i-4] == 0:
                                board[i-4] = board[i]
                                board[i] = 0
                                changed = True

            if arrow == 2: #down
                for iter in range(0,3):
                    for i in range(0,12,1):
                        if not board[i] == 0:
                            if board[i+4] == 0:
                                board[i+4] = board[i]
                                board[i] = 0
                                changed = True
                for i in range(11,0,-1):
                    if not board[i] == 0:
                        if board[i+4] == board[i]:
                            change += board[i]*2
                            board[i+4] = board[i]*2
                            board[i] = 0
                for iter in range(0,3):
                    for i in range(0,12,1):
                        if not board[i] == 0:
                            if board[i+4] == 0:
                                board[i+4] = board[i]
                                board[i] = 0
                                changed = True

            if arrow == 3: #right
                for iter in range(0,3):
                    for i in range(0,15,1):
                        if not (i % 4 == 3 or board[i] == 0):
                            if board[i+1] == 0:
                                board[i+1] = board[i]
                                board[i] = 0
                                changed = True
                for i in range(14,0,-1):
                    if not i % 4 == 3 or board[i] == 0:
                        if board[i+1] == board[i]:
                            change += board[i]*2
                            board[i+1] = board[i]*2
                            board[i] = 0
                for iter in range(0,3):
                    for i in range(0,15,1):
                        if not i % 4 == 3 or board[i] == 0:
                            if board[i+1] == 0:
                                board[i+1] = board[i]
                                board[i] = 0
                                changed = True
            
            score += change
            return score, change != 0 or changed is True, change

        spawn_random()
        while True:
            if changed:
                embed = discord.Embed(title="2048", color=color)

                spawn_random()
                output = ""
                i = 0
                
                if badinternet is True:
                    value = ""
                    i = 0
                    for field in board:
                        if field == 0:
                            field = ""
                        for o in range(0,5-len(str(field))):
                            value += " "
                        value += f"{field} |"
                        if i%4 == 3:
                            value+="\n"
                        i += 1
                else:
                    id = graphic()
                    if zug_nr == 0:
                        fileschannel = await self.client.fetch_channel(828285573860163595)
                    filemessage = await fileschannel.send(file=discord.File(f'temp_files/2048-{id}.png'))
                    
                    embed.set_image(url=filemessage.attachments[0].url)

                game_over = False
                if not 0 in board:
                    for i in range(0,16,1):
                        if not (i % 4 == 0 or board[i] == 0):
                            if board[i-1] == board[i]:
                                break
                        if i > 3:
                            if not board[i] == 0:
                                if board[i-4] == board[i]:
                                    break
                        if i == 15:
                            game_over = True
                            embed.description = "**Game over!** React with ↩️ to play again!"                            

                embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
                embed.set_footer(text="Play the original game at www.play2048.co")
                if change is None:
                    embed.add_field(name="Score:", value=f"```cs\n{score}```")
                else:
                    if highscore < score:
                        highscore = score
                        with open("json_files/2048highscores.json", "r") as h:
                            highscores = json.load(h)

                        highscores[str(ctx.author.id)] = highscore
                        with open("json_files/2048highscores.json", "w") as h:
                            json.dump(highscores, h, indent=4)

                    embed.add_field(name="Score:", value=f"```cs\n{score} (+{change})```")
                embed.add_field(name="Personal best:", value=f"```cs\n{highscore}```")

                if badinternet is True:
                    embed.add_field(name="Board:", value="```" + value + "```", inline=False)
                else:
                    os.remove(f'temp_files/2048-{id}.png')

                if zug_nr == 0:
                    message = await ctx.send(embed=discord.Embed(title="Please wait ...", color=discord.Color.random()))
                    for emoji in arrows:
                        await message.add_reaction(emoji)
                await message.edit(embed=embed)

                if game_over is True:
                    await message.clear_reactions()
                    await message.add_reaction("↩️")

                    def check(reaction, user):
                        return (
                            reaction.message.id == message.id
                            and user.id == ctx.author.id
                            and str(reaction.emoji) == "↩️"
                        )

                    reaction, user = await self.client.wait_for(
                        "reaction_add", check=check
                    )


                    score = 0
                    board = [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]
                    spawn_random()
                    zug_nr = 0
                    change = None
                    changed = True
                    win = False
                    game_over = False
                    continue
                    
            def check(reaction, user):
                return (
                    reaction.message.id == message.id
                    and user.id == ctx.author.id
                    and str(reaction.emoji) in arrows
                )

            reaction, user = await self.client.wait_for(
                "reaction_add", check=check
            )

            await reaction.remove(user)
            arrow = arrows.index(str(reaction.emoji))
            score, changed, change = process(arrow, score)
            zug_nr += 1

            if 2048 in board and win is False:
                await ctx.channel.send(f"GG {ctx.author.mention}, you got the **2048 tile!** <:2048:828333452813795348> Well done!")
                win = True

    @commands.command(
        enabled=False,
        hidden=True,
        description="This command is not ready to use yet.",
        aliases=["schach"],
    )
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def chess(self, ctx, opponent: discord.Member):
        board, turn, won, spiel, channel = (
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            0,
            0,
            2,
            [ctx.channel],
        )
        accepted = await challenge(self, ctx.author, opponent, spiel, channel)
        if accepted:
            if randint(0, 1) == 0:
                players = [ctx.author, opponent]
            else:
                players = [opponent, ctx.author]

            message = await create_emojis(
                channel, react_emojis[spiel], "The game is starting ...", players
            )
            content = chess.update(board)
            await create_card(
                players[0], players[1], spiel, content, turn, won, message, players
            )
            await ingame(self, channel, players, board, turn, spiel, message)

    @commands.command(
        enabled=True,
        hidden=True,
        description="Play othello against a server member!",
        aliases=["reversi"],
    )
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def othello(self, ctx, opponent: discord.Member):
        board, turn, won, spiel, channel = (
            [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                2,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                1,
                2,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ],
            0,
            0,
            3,
            [ctx.channel],
        )
        accepted = await challenge(self, ctx.author, opponent, spiel, channel)
        if accepted:
            if randint(0, 1) == 0:
                players = [ctx.author, opponent]
            else:
                players = [opponent, ctx.author]

            message = await create_emojis(
                channel, react_emojis[spiel], "The game is starting ...", players
            )
            possible_moves, i = {}, 0
            for item in board:
                possible, possblties = othello.process_check_field(board, i, 1)
                if possible:
                    possible_moves[i] = possblties
                i += 1
            content = othello.update(board, possible_moves)
            await create_card(
                players[0],
                players[1],
                spiel,
                content,
                turn,
                won,
                message,
                players,
                default_possible_moves=possible_moves,
            )
            await ingame(
                self,
                channel,
                players,
                board,
                turn,
                spiel,
                message,
                default_possible_moves=possible_moves,
            )

    @commands.Cog.listener()
    @othello.error
    async def othello_open(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            board, turn, won, spiel, channel = (
                [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    2,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                    2,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                ],
                0,
                0,
                3,
                [ctx.channel],
            )
            opponent, accepted = await open_game(self, ctx.author, spiel, ctx.channel)
            if accepted:
                if randint(0, 1) == 0:
                    players = [ctx.author, opponent]
                else:
                    players = [opponent, ctx.author]

                message = await create_emojis(
                    channel,
                    react_emojis[spiel],
                    f"{opponent.name} joined! The game is starting ...",
                    players,
                )
                possible_moves, i = {}, 0
                for item in board:
                    possible, possblties = othello.process_check_field(board, i, 1)
                    if possible:
                        possible_moves[i] = possblties
                    i += 1
                content = othello.update(board, possible_moves)
                await create_card(
                    players[0],
                    players[1],
                    spiel,
                    content,
                    turn,
                    won,
                    message,
                    players,
                    default_possible_moves=possible_moves,
                )
                await ingame(
                    self,
                    channel,
                    players,
                    board,
                    turn,
                    spiel,
                    message,
                    default_possible_moves=possible_moves,
                )

    @commands.command(
        help="If you don't mention an opponent, an open game anyone can join will be started.",
        description="Play tictactoe against a server member! \nThis command starts a local tictactoe game.",
        aliases=["tic-tac-toe"],
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def tictactoe(self, ctx, opponent: discord.Member=None):
        if opponent is None:
            board, turn, won, spiel, channel = (
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                0,
                0,
                0,
                [ctx.channel],
            )
            opponent, accepted = await open_game(self, ctx.author, spiel, ctx.channel)
            if accepted:
                if randint(0, 1) == 0:
                    players = [ctx.author, opponent]
                else:
                    players = [opponent, ctx.author]

                message = await create_emojis(
                    channel,
                    react_emojis[spiel],
                    f"{opponent.name} joined! The game is starting ...",
                    players,
                )
                content = tictactoe.update(board)
                await create_card(
                    players[0], players[1], spiel, content, turn, won, message, players
                )
                await ingame(self, channel, players, board, turn, spiel, message)
        else:
            board, turn, won, spiel, channel = (
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                0,
                0,
                0,
                [ctx.channel],
            )
            accepted = await challenge(self, ctx.author, opponent, spiel, channel)
            if accepted:
                if randint(0, 1) == 0:
                    players = [ctx.author, opponent]
                else:
                    players = [opponent, ctx.author]

                message = await create_emojis(
                    channel, react_emojis[spiel], "The game is starting ...", players
                )
                content = tictactoe.update(board)
                await create_card(
                    players[0], players[1], spiel, content, turn, won, message, players
                )
                await ingame(self, channel, players, board, turn, spiel, message)


    @commands.command(
        help="If you don't mention an opponent, an open game anyone can join will be started.",
        description="Play connect4 against a server member!\nThis command starts a local connect4 game.",
        aliases=["connect-4", "viergewinnt", "4gewinnt"],
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def connect4(self, ctx, opponent: discord.Member=None):
        if opponent is None:
            board, turn, won, spiel, channel = (
                [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                ],
                0,
                0,
                1,
                [ctx.channel],
            )
            opponent, accepted = await open_game(self, ctx.author, spiel, ctx.channel)
            if accepted:
                if randint(0, 1) == 0:
                    players = [ctx.author, opponent]
                else:
                    players = [opponent, ctx.author]

                message = await create_emojis(
                    channel,
                    react_emojis[spiel],
                    f"{opponent.name} joined! The game is starting ...",
                    players,
                )
                content = viergewinnt.update(board)
                await create_card(
                    players[0], players[1], spiel, content, turn, won, message, players
                )
                await ingame(self, channel, players, board, turn, spiel, message)
        else:        
            board, turn, won, spiel, channel = (
                [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                ],
                0,
                0,
                1,
                [ctx.channel],
            )
            accepted = await challenge(self, ctx.author, opponent, spiel, channel)
            if accepted:
                if randint(0, 1) == 0:
                    players = [ctx.author, opponent]
                else:
                    players = [opponent, ctx.author]

                message = await create_emojis(
                    channel, react_emojis[spiel], "The game is starting ...", players
                )
                content = viergewinnt.update(board)
                await create_card(
                    players[0], players[1], spiel, content, turn, won, message, players
                )
                await ingame(self, channel, players, board, turn, spiel, message)

    @commands.command(
        brief="Starts a global connect4 game (across servers)",
        name="global-connect4",
        description="Starts a global Connect4 game.\nIf someone else runs the command, you'll be matched with them.",
        aliases=[
            "gconnect4",
            "globalconnect4",
            "globalviergewinnt",
            "global-viergewinnt",
            "global4gewinnt",
            "global-4gewinnt",
        ],
    )
    @commands.bot_has_permissions(manage_messages=True)
    async def globalconnect4(self, ctx):
        author = ctx.author
        author: discord.User
        spiel = 1
        keys = list(self.gconnect4.keys())
        self.gconnect4, msg, channel, players, cont = await global_game(
            self, self.gconnect4, ctx, self.gconnect4, spiel, keys
        )
        if cont:
            board, turn, won = (
                [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                ],
                0,
                0,
            )
            content = viergewinnt.update(board)
            if len(channel) == 1:
                await create_card(
                    players[0], players[1], spiel, content, turn, won, msg, players
                )
                await ingame(self, channel, players, board, turn, spiel, msg)
            else:
                try:
                    self.gconnect4.pop(msg)
                except Exception:
                    pass
                await create_card(
                    players[0], players[1], spiel, content, turn, won, msg, players
                )
                await ingame(self, channel, players, board, turn, spiel, msg)
        elif not msg is None:
            await asyncio.sleep(2700)
            if msg in self.gconnect4:
                self.gconnect4.pop(msg)
                try:
                    await msg.edit(
                        content=ctx.author.mention,
                        embed=discord.Embed(
                            title="🌍 Timeout",
                            description=f"{ctx.author.mention} started a global **{spiele[spiel]}** game, but nobody joined within 45 minutes. The game has been cancelled.",
                            color=discord.Colour.blue(),
                        ),
                    )
                except Exception:
                    pass

    @commands.command(
        name="global-tictactoe",
        brief="Starts a global TicTacToe game (across servers)",
        description="Starts a global TicTacToe game.\nIf someone else runs the command, you'll be matched with them.",
        aliases=["gtictactoe", "globaltictactoe"],
    )
    @commands.bot_has_permissions(manage_messages=True)
    async def globaltictactoe(self, ctx):
        author = ctx.author
        author: discord.User
        spiel = 0
        keys = list(self.gtictactoe.keys())
        self.gtictactoe, msg, channel, players, cont = await global_game(
            self, self.gtictactoe, ctx, self.gtictactoe, spiel, keys
        )
        if cont:
            board, turn, won = [0, 0, 0, 0, 0, 0, 0, 0, 0], 0, 0
            content = tictactoe.update(board)
            if len(channel) == 1:
                await create_card(
                    players[0], players[1], spiel, content, turn, won, msg, players
                )
                await ingame(self, channel, players, board, turn, spiel, msg)
            else:
                try:
                    self.gtictactoe.pop(msg)
                except Exception:
                    pass
                await create_card(
                    players[0], players[1], spiel, content, turn, won, msg, players
                )
                await ingame(self, channel, players, board, turn, spiel, msg)
        elif not msg is None:
            await asyncio.sleep(2700)
            if msg in self.gtictactoe:
                self.gtictactoe.pop(msg)
                try:
                    await msg.edit(
                        content=ctx.author.mention,
                        embed=discord.Embed(
                            title="🌍 Timeout",
                            description=f"{ctx.author.mention} started a global **{spiele[spiel]}** game, but nobody joined within 45 minutes. The game has been cancelled.",
                            color=discord.Colour.blue(),
                        ),
                    )
                except Exception:
                    pass


async def global_game(self, glist, ctx, ggl, spiel, keys):
    key = None
    for item in keys:
        if ggl[item] == ctx.author:
            await ctx.send(f"You already started another global {spiele[spiel]} game!")
            return ggl, None, None, None, False
        else:
            key = item
    if key is None:
        embed = discord.Embed(
            title="Waiting for another player ...",
            description="As soon as someone else runs the command, you'll be matched with them!",
            color=get_client_color(ctx),
        )
        embed.set_author(
            name=f"🌍 Global {spiele[spiel]}", icon_url=ctx.author.avatar_url
        )
        embed.set_footer(text="🏓 You'll be notified when you have been matched.")
        msg = await ctx.send(None, embed=embed)
        ggl[msg] = ctx.author
        return ggl, msg, None, None, False
    else:
        channel, players = [ctx.channel, key.channel], [ctx.author, glist[key]]
        ggl.pop(key)
        await key.delete()
        if channel[0] == channel[1]:
            channel = [channel[0]]
            msg = await create_emojis(
                channel, react_emojis[spiel], "The game is starting ...", players
            )
        else:
            msg = await create_emojis(
                channel, react_emojis[spiel], "You have been matched with {}!", players
            )
        return ggl, msg, channel, players, True


async def open_game(self, author, spiel, channel):
    chal = discord.Embed(
        title=f"{author} started an open game!",
        description="React with 👍 if you want to join!",
        color=discord.Colour.green(),
    )
    chal.set_author(
        name=header_emojis[spiel] + " " + spiele[spiel], icon_url=author.avatar_url
    )
    message = await channel.send(None, embed=chal)
    await message.add_reaction("👍")

    def check(reaction, user):
        return reaction.message.id == message.id and str(reaction.emoji) == "👍"

    while True:
        try:
            reaction, user = await self.client.wait_for(
                "reaction_add", timeout=180.0, check=check
            )
        except asyncio.TimeoutError:
            await message.clear_reactions()
            await message.edit(
                content=None,
                embed=discord.Embed(
                    title=":alarm_clock: Timeout",
                    description=f"{author.mention} started an open **{spiele[spiel]}** game, but noone joined in time.",
                    color=discord.Colour.red(),
                ),
            )
            return None, False
        else:
            if not (user.bot or user == author):
                await message.delete()
                return user, True
            elif user == author:
                await reaction.remove(user)


async def challenge(self, author, opponent, spiel, channel):
    if author.id == opponent.id:
        await channel[0].send("Don't try to challenge yourself! :laughing:")
        return False
    elif opponent.bot:
        await channel[0].send(f"Bots can't play {spiele[spiel]}!")
        return False
    else:
        chal = discord.Embed(
            title=f"{author} challenged you!",
            description=f"Do you want to accept?",
            color=discord.Color.teal(),
        )
        chal.set_author(
            name=header_emojis[spiel] + " " + spiele[spiel], icon_url=author.avatar_url
        )
        message = await channel[0].send(f"{opponent.mention}", embed=chal)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check(reaction, user):
            return True(
                reaction.message.id == message.id
                and str(reaction.emoji) in ["✅", "❌"]
                and user.id == opponent.id
            )

        try:
            reaction, user = await self.client.wait_for(
                "reaction_add", timeout=180.0, check=check
            )
        except asyncio.TimeoutError:
            await message.clear_reactions()
            await message.edit(
                content=None,
                embed=discord.Embed(
                    title=":alarm_clock: Timeout",
                    description=f"{author.mention} wanted  to play **{spiele[spiel]}** against {opponent.mention}, but {opponent.mention} didn't answer in time.",
                    color=discord.Colour.red(),
                ),
            )
        else:
            if str(reaction.emoji) == "✅":
                await message.delete()
                return True
            else:
                await message.clear_reactions()
                await message.edit(
                    content=author.mention,
                    embed=discord.Embed(
                        title="Challenge denied",
                        description=f"{opponent} denied {author}'s challenge.",
                        color=discord.Colour.red(),
                    ),
                )
                return False


async def ingame(
    self,
    channel,
    players,
    default_board,
    default_turn,
    spiel,
    message,
    *,
    default_possible_moves=None,
):
    possible_moves = default_possible_moves
    won = 0
    step = 0
    board = default_board
    turn = default_turn

    def check(reaction, user):
        fix = False
        for item in message:
            if reaction.message.id == item.id:
                fix = True
                break

        return fix


    while True:
        try:
            reaction, user = await self.client.wait_for(
                "reaction_add", timeout=180.0, check=check
            )
        except asyncio.TimeoutError:
            if turn == 0:
                other_user = players[1]
            else:
                other_user = players[0]
            card = message[0].embeds[0]
            card.set_field_at(
                len(card.fields) - 1,
                name=f"⏰ {players[turn].name} didn't react in time",
                value=f"{other_user.mention} automatically wins",
                inline=False,
            )
            for item in channel:
                await item.send(
                    embed=discord.Embed(
                        title=f"⏰ {players[turn].name} didn't react in time!",
                        description=f"Therefore, {other_user.mention} automatically wins!",
                        color=discord.Colour.random(),
                    )
                )
            for item in message:
                await item.edit(content=None, embed=card)
                await item.clear_reactions()
            return
        else:
            if (
                user.id == players[turn].id
                and str(reaction.emoji) in react_emojis[spiel]
            ):
                field = react_emojis[spiel].index(str(reaction.emoji))
                await reaction.remove(user)
                if spiel == 0:
                    board, turn, won = tictactoe.process(board, turn + 1, field)
                    turn = turn - 1
                    content = tictactoe.update(board)
                    await create_card(
                        players[0],
                        players[1],
                        spiel,
                        content,
                        turn,
                        won,
                        message,
                        players,
                    )
                if spiel == 1:
                    board, turn, won = viergewinnt.process(board, turn + 1, field)
                    turn = turn - 1
                    content = viergewinnt.update(board)
                    await create_card(
                        players[0],
                        players[1],
                        spiel,
                        content,
                        turn,
                        won,
                        message,
                        players,
                        field,
                    )
                """if spiel == 2:
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
            step = 0"""
                if spiel == 3:
                    board, turn, won, possible_moves = othello.process(
                        board, turn + 1, field, possible_moves
                    )
                    turn = turn - 1
                    content = othello.update(board, possible_moves)
                    await create_card(
                        players[0],
                        players[1],
                        spiel,
                        content,
                        turn,
                        won,
                        message,
                        players,
                        field,
                        default_possible_moves=possible_moves,
                    )
                if won != 0:
                    return
            else:
                await reaction.remove(user)


async def create_emojis(channel, emojis, text, players):
    message, i = [], 0
    if len(channel) == 1:
        message.append(
            await channel[0].send(
                f"{players[0].mention} {players[1].mention}",
                embed=discord.Embed(title=text, color=discord.Colour.random()),
            )
        )
    elif len(channel) == 2:
        message.append(
            await channel[0].send(
                f"{players[0].mention}",
                embed=discord.Embed(
                    title=text.format(players[1]), color=discord.Colour.random()
                ),
            )
        )
        message.append(
            await channel[1].send(
                f"{players[1].mention}",
                embed=discord.Embed(
                    title=text.format(players[0]), color=discord.Colour.random()
                ),
            )
        )
    for e in emojis:
        for item in message:
            await item.add_reaction(e)
    return message


async def create_card(
    p1,
    p2,
    spiel,
    content,
    turn,
    won,
    message,
    players,
    highlight=None,
    *,
    step=1,
    default_possible_moves=None,
):
    card = discord.Embed(title=spiele[spiel], color=turncolors[spiel][turn])
    az = ["❖", "❖"]
    if spiel == 0:
        card.add_field(name="Board:", value=f"{content}{emojis['spacer']}")
        card.add_field(name="** **", value="** **")
    elif spiel == 1:
        if highlight is None:
            card.add_field(
                name="Board:", value=f"{emojis['spacer']}{content}\n{emojis['spacer']}"
            )
        else:
            header = ""
            for i in range(7):
                if i == highlight:
                    header = f"{header}🔽"
                else:
                    header = f"{header}{emojis['spacer']}"
            card.add_field(
                name="Board:", value=f"{header}{content}\n{emojis['spacer']}"
            )
    else:
        card.description = content
    if len(message) == 1:
        card.set_author(name="🏠 Local game", icon_url=message[0].guild.icon_url)
        card.add_field(
            name="Players:",
            value=f"{az[0]} **{str(p1)}** {symbols[spiel][0]}\n\n{az[1]} **{str(p2)}** {symbols[spiel][1]}\n{emojis['spacer']}",
            inline=True,
        )
    elif len(message) == 2:
        card.set_author(name="🌍 Global game", icon_url=message[turn].guild.icon_url)
        card.add_field(
            name="Players:",
            value=f"{az[0]} **{str(p1)}** {symbols[spiel][0]}\n*Server: {message[0].guild}*\n\n{az[1]} **{str(p2)}** {symbols[spiel][1]}\nServer: *{message[1].guild}*\n{emojis['spacer']}",
            inline=True,
        )
    if won != 0:
        if won == 3:
            card.add_field(name="➤ Tie!", value="** **", inline=False)
            for item in message:
                await item.clear_reactions(), await won_message(
                    3, item.channel, None, len(message)
                )
        else:
            card.add_field(
                name=f"➤ {players[won-1].name} won!", value="** **", inline=False
            )
            gewinn = randint(14, 25)
            for item in message:
                await item.clear_reactions(), await won_message(
                    players[won - 1], item.channel, gewinn, len(message)
                )
    elif spiel == 0:
        card.add_field(
            name=f"➤ {players[turn].name}, it's your turn!",
            value="Please select an empty field.",
            inline=False,
        )
    elif spiel == 1:
        card.add_field(
            name=f"➤ {players[turn].name}, it's your turn!",
            value="Please select a column.",
            inline=False,
        )
    # elif spiel == 2: card.add_field(name=f"➤ {players[turn].name}, it's your turn!", value="Select the column of the paw you want to move.\n**(A - H)**\n\n\_ \_ - \_ \_", inline=False)
    elif spiel == 3:
        card.add_field(
            name=f"➤ {players[turn].name}, it's your turn!",
            value="Please select one of the marked fields.",
            inline=False,
        )
        card.set_footer(text="Warning: Othello is still in beta testing.")
    for item in message:
        await item.edit(content=None, embed=card)


async def won_message(winner, channel, gewinn, servers):
    if winner == 3:
        embed = discord.Embed(title="Tie!", color=discord.Colour.random())
        if servers == 1:
            embed.description = "**Nobody** gained XP."
        await channel.send(None, embed=embed)
    else:
        embed = discord.Embed(
            title=f"{winner} won! :tada:", color=discord.Colour.random()
        )
        if servers == 1:
            with open("json_files/leveling.json", "r") as d:
                servers = json.load(d)
            xp = servers[str(channel.guild.id)][str(winner.id)]["xp"]
            servers[str(channel.guild.id)][str(winner.id)]["xp"] = xp + gewinn

            with open("json_files/leveling.json", "w") as d:
                json.dump(servers, d, indent=4)
            embed.title, embed.description, = (
                f"You won, {winner.name}! :tada:",
                f"You gained **{gewinn} XP.**",
            )
            await channel.send(winner.mention, embed=embed)
        else:
            await channel.send(None, embed=embed)


# activate cogs


def setup(client):
    client.add_cog(minigames(client))
