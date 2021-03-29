symbols = ["🟩","<:ob:820401371865939968>","<:ow:820401476047863838>"]
numbers=["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","0️⃣","<:a_:817909368765939722>","<:b_:817909368594235434>","<:c_:817909369026772993>","<:d_:817909368941969449>","<:e_:817909369316048926>","<:f_:817909368997281794>","<:g_:817909369186287666>","<:h_:817909369173704734>"]
from main import emojis

def update(board, possible_moves):
  send = ""
  i,o = 0,0
  for item in board:
    if i in list(possible_moves.keys()): send = f"{send}{numbers[o]}"; o+=1
    else: send = f"{send}{symbols[item]}"
    i += 1
    if i%8 == 0:
      send = f"{send}\n"
  return send+emojis['spacer']

def process(board, old_turn, input, last_possible_moves):
  field = list(last_possible_moves.keys())[input]
  board[field] = old_turn
  for key in list(last_possible_moves[field].keys()):
    if last_possible_moves[field][key] == 1:
      i = 1
      while not board[field+key*i] == old_turn:
        board[field+key*i] = old_turn
        i +=1
  turn = abs(old_turn-3)
  possible_moves,i = {},0

  for item in board:
    possible, possblties = process_check_field(board, i, turn)
    if possible:
      possible_moves[i] = possblties
    i += 1


  if possible_moves == {}:
    turn = old_turn
    possible_moves,i = {},0
    for item in board:
      possible, possblties = process_check_field(board, i, turn)
      if possible:
        possible_moves[i] = possblties
      i += 1
    if possible_moves == {}:
      return board, old_turn, 3, {}
  #  else: return board, abs(old_turn-3), 0, possible_moves
    else: return board, old_turn, 0, possible_moves

  return board, turn, 0, possible_moves

def process_check_field(board, field, color):
  possible = False
  possblties = {-8:0, 8:0, -1:0, 1:0, 7:0, 9:0, -9:0,-7:0}
  if board[field] == 0:

    c = 8
    if process_direction(c, 8, board, field, color): possblties[c] = 1; possible=True
    c = -8
    if process_direction(c, 8, board, field, color): possblties[c] = 1; possible=True
    c = -1
    if process_direction(c, 7, board, field, color): possblties[c] = 1; possible=True
    c = 1
    if process_direction(c, 0, board, field, color): possblties[c] = 1; possible=True

    c = 7
    if process_direction(c, 7, board, field, color): possblties[c] = 1; possible=True
    c = 9
    if process_direction(c, 0, board, field, color): possblties[c] = 1; possible=True
    c = -9
    if process_direction(c, 7, board, field, color): possblties[c] = 1; possible=True
    c = -7
    if process_direction(c, 0, board, field, color): possblties[c] = 1; possible=True

  return possible, possblties


def process_direction(c, edge, board, field, color):
  try:
    if not (field+c)%8 == edge:
      pos = field + c
      i = 0
      while board[pos] == abs(color-3):
        pos += c
        if pos%8 == edge: break
        i += 1
      if board[pos] == color and i > 0 and not pos%8 == edge: return True
  except IndexError: pass
  return False

'''
while True:
  update(board, possible_moves)
  
  if won != 0:
    if won == 3:
      print("Draw!")
      break
    else:
      print(f"Player {won} won!")
      break
 
  if turn==1: print("It's Player 1's turn!\n")
  else: print("It's Player 2's turn!\n")
  field = input("Please select one of the marked fields.")
  turn, won, possible_moves = process(board, int(turn), int(field)-1, possible_moves)
'''
