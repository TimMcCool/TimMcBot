import discord
import threading
import flask
from flask import Flask, render_template, send_file, request
from threading import Thread
import random
import json
import pandas as pd
import extensions
from replit import db

app = Flask("")

def ranklist(data):
    keys = list(data.keys())

    def check(elem):
        return dict(data[elem])["xp"]

    sorted_keys = sorted(list(data.keys()), key=check, reverse=True)
    sorted_values = []

    for key in sorted_keys:
        dict(data[key])["id"] = key
        sorted_values.append(data[key])

    return sorted_values

@app.route("/")
def index():
    return "Your bot is alive."

@app.route('/api/lb/', defaults={"guild": None})
def api_lb(guild):
    if not guild:
        guild = request.args.get("guild")
    try:
        leveling = dict(db['leveling'])
        data = dict(leveling[str(guild)])
        for item in data:
            data[item] = dict(data[item])
            data[item]['daily'] = dict(data[item]['daily'])
            data[item]['weekly'] = dict(data[item]['weekly'])
        response = app.response_class(
            response=json.dumps(ranklist(data), indent=4),
            status=200,
            mimetype='application/json'
        )
        
    except Exception:
        response = app.response_class(
            response=json.dumps({"error" : "NoDataAvailable"}, indent=4),
            status=200,
            mimetype='application/json'
        )    
    return response


@app.route('/api/polls/list/', defaults={"guild": None})
def polls_list(guild):
    if not guild:
        guild = request.args.get("guild")
    try:
        with open("json_files/polls.json", "r") as d:
            data = list(json.load(d)[str(guild)].keys())
    except KeyError:
        data = {"error" : "NoDataAvailable"}
    response = app.response_class(
        response=json.dumps(data, indent=4),
        status=200,
        mimetype='application/json'
    )
    return response  


@app.route('/dev/guilds')
def guilds():
    data = list(dict(db['leveling']).keys())
    response = app.response_class(
        response=json.dumps(data, indent=4),
        status=200,
        mimetype='application/json'
    )
    return response    





def api(file, guild, arg="guild"):
    if not guild:
        guild = request.args.get(arg)
    try:
        with open(file, "r") as d:
            data = json.load(d)[str(guild)]
    except KeyError:
        data = {"error" : "NoDataAvailable"}
    response = app.response_class(
        response=json.dumps(data, indent=4),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/api/levelroles/', defaults={"guild": None})
def api_lr(guild):
    return api("json_files/levelroles.json", guild)

@app.route('/api/prefixes/', defaults={"guild": None})
def api_prefixes(guild):
    return api("json_files/prefixes.json", guild)

@app.route('/api/giveaway/', defaults={"message": None})
def api_giveaway_info(message):
    return api("json_files/giveaways.json", message, "message")


@app.route("/leaderboard/", defaults={"guild": None, "style": None})
@app.route("/lb/", defaults={"guild": None, "style": None})
def leaderboard(guild, style):
    if not guild:
        guild = request.args.get("guild")
    if not style:
        style = request.args.get("style")
    if not guild:
        return "No guild id provided."
    else:
        leveling = dict(db['leveling'])
        try:
            data = dict(leveling[str(guild)])
        except Exception:
            return "No data available for this guild."

        from extensions import leveling
        t = ranklist(data)

        # creates dict
        leaderboard = {}
        i = 0

        for item in t:
            i += 1
            if i <= 3:
                symbol = "🥇🥈🥉"[i - 1]
            else:
                symbol = "#" + str(i)
            leaderboard[item["name"]] = [
                f"{item['messages']}",
                f"{item['xp']} XP",
                str(leveling.getlevel(item["xp"])[0]),
                symbol,
            ]
        guild_object = client.get_guild(int(guild))
        if guild_object is None:
            guild_name = "Unknown Guild"
        else:
            guild_name = guild_object.name

    if style == "new":
        return render_template(
            "new_leaderboard.html", guild=guild, guild_name=guild_name, data=leaderboard
        )
    else:
        return render_template(
            "leaderboard.html", guild=guild, guild_name=guild_name, data=leaderboard
        )


def run():
    app.run(host="0.0.0.0", port=random.randint(2000, 9000))

leveling = {}
def keep_alive():
    from main import client

    global client
    server = Thread(target=run)
    server.start()