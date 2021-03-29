import discord
import threading
import flask
from flask import Flask, render_template, request
from threading import Thread
import random
import json
import pandas as pd
import extensions

app = Flask('')

@app.route("/")
def index():
	return "Your bot is alive!"

@app.route('/leaderboard/', defaults={'guild': None})
def generate_user(guild):
  if not guild:
    guild = request.args.get('guild')

  if not guild:
    #return render_template('index.html')
    return "No guild id provided."
  
  else:
    with open("json_files/leveling.json", "r") as d:
      servers = json.load(d)

    if str(guild) in servers:
      data = servers[str(guild)]
    else:
      return "No data available for this guild."

    #sort data
    keys = list(data.keys())
    tbefore=[]
    for item in keys:
      tbefore.append([data[item],item])

    def check(elem):
      return elem[0]["xp"]
    
    t = sorted(tbefore, key=check, reverse=True)

    #creates dict
    leaderboard = {}
    i = 0
    from extensions import leveling
    for item in t:
      i += 1
      if i <= 3:
        symbol = "🥇🥈🥉"[i-1]
      else:
        symbol = "#"+str(i)
      leaderboard[item[0]['name']] = [f"{item[0]['messages']}", f"{item[0]['xp']} XP", str(leveling.getlevel(item[0]['xp'])[0]), symbol] 
    
    guild_object = client.get_guild(int(guild))
    if guild_object is None:
      guild_name = "Unknown Guild"
    else:
      guild_name = guild_object.name

    #creates html dataframe from dict
    html_data = pd.DataFrame.from_dict(leaderboard)
        
  return render_template('leaderboard.html', guild=guild, guild_name=guild_name, data=leaderboard)

def run():
  app.run(host="0.0.0.0", port=random.randint(2000, 9000))

def keep_alive():
  from main import client
  global client
  server = Thread(target=run)
  server.start()

