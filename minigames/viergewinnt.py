symbols = ["⚫","🔴","🟡"]
numbers = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣"]
from main import emojis

def update(data):
  send = ""
  i = 0
  for item in data:
    i += 1
    send = f"{send}{symbols[item]}"
    if i%7 == 0:
      send = f"{send}{emojis['spacer']}{emojis['spacer']}\n"
  for i in range(0,7):
    send = f"{send}{numbers[i]}"
  return f"\n{send}"

def process(data, old_turn, column):
  turn = old_turn
  for i in range(0,7):
    field = column+35-i*7
    if data[field] == 0:
      data[field] = turn

      i = 0
      while data[field+i] == turn and not ((field+i)%7 == 6 and i!=0):
        i-=1
        if field+i < 0: break
      length=abs(i)
      i = 0
      while data[field+i] == turn and not ((field+i)%7 == 0 and i!=0):
        i+=1
        if field+i > 41: break
      length += i
      if length >= 5:
        return data, turn, turn

      i = 0
      while data[field+i] == turn:
        i-=7
        if field+i < 0: break
      length=abs(i)/7
      i = 0
      while data[field+i] == turn:
        i+=7
        if field+i > 41: break
      length += i/7
      if length >= 5:
        return data, turn, turn

      i = 0
      while data[field+i] == turn and not ((field+i)%7 == 6 and i!=0):
        i-=8
        if field+i < 0: break
      length=abs(i)/8
      i = 0
      while data[field+i] == turn and not ((field+i)%7 == 0 and i!=0):
        i+=8
        if field+i > 41: break
      length += i/8
      if length >= 5:
        return data, turn, turn

      i = 0
      while data[field+i] == turn and not ((field+i)%7 == 0 and i!=0):
        i-=6
        if field+i < 0: break
      length=abs(i)/6
      i = 0
      while data[field+i] == turn and not ((field+i)%7 == 6 and i!=0):
        i+=6
        if field+i > 41: break
      length += i/6
      if length >= 5:
        return data, turn, turn

      if not 0 in data: return data, turn, 3

      if turn == 1: turn = 2
      else: turn = 1
      return data, turn, 0

  return data, turn, 0


