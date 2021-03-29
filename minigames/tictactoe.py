symbols = "⚫❌⭕"
numbers = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]
from main import emojis

def update(board):
  send = ""
  i = 0
  for item in board:
    i += 1
    if item == 0: send = f"{send}{numbers[i-1]}"
    else: send = f"{send}{symbols[item]}"
    if i%3 == 1: send = f"{send}"
    if i%3 == 2: send = f"{send}"
    if i%3 == 0 and not i == 9: send = f"{send}\n"
  return f"```{send}```"


def process(data, old_turn, field):
  turn = old_turn
  if data[field] == 0: data[field] = turn
  else: return data, turn, 0
  
  i = 0
  while True:
    if data[i] != turn: break
    i=i+1
    if i == 3: return data, turn, turn
  i = 3
  while True:
    if data[i] != turn: break
    i=i+1
    if i == 6: return data, turn, turn
  i = 6
  while True:
    if data[i] != turn: break
    i=i+1
    if i == 9: return data, turn, turn

  i = 0
  while True:
    if data[i] != turn: break
    i=i+3
    if i == 9: return data, turn, turn
  i = 1
  while True:
    if data[i] != turn: break
    i=i+3
    if i == 10: return data, turn, turn
  i = 2
  while True:
    if data[i] != turn: break
    i=i+3
    if i == 11: return data, turn, turn

  i = 0
  while True:
    if data[i] != turn: break
    i=i+4
    if i == 12: return data, turn, turn
  i = 2
  while True:
    if data[i] != turn: break
    i=i+2
    if i == 8: return data, turn, turn

  if not 0 in data: return data, turn, 3

  if turn == 2: turn = 1
  else: turn = 2

  return data, turn, 0

