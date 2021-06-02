import discord
import threading
import flask
from flask import Flask, render_template, send_file, request
from threading import Thread
import random
import json
import pandas as pd
import extensions

app = Flask("")

def ranklist(data):
    keys = list(data.keys())

    def check(elem):
        return data[elem]["xp"]

    sorted_keys = sorted(list(data.keys()), key=check, reverse=True)
    sorted_values = []

    for key in sorted_keys:
        data[key]["id"] = key
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
        with open("json_files/leveling.json", "r") as d:
            data = json.load(d)[str(guild)]
        response = app.response_class(
            response=json.dumps(ranklist(data), indent=4),
            status=200,
            mimetype='application/json'
        )
    except Exception:
        response = app.response_class(
            response=json.dumps([], indent=4),
            status=200,
            mimetype='application/json'
        )    
    return response

def api(file, guild):
    if not guild:
        guild = request.args.get("guild")
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


@app.route('/dev/guilds')
def guilds():
    with open("json_files/leveling.json", "r") as d:
        data = list(json.load(d).keys())
    response = app.response_class(
        response=json.dumps(data, indent=4),
        status=200,
        mimetype='application/json'
    )
    return response    

@app.route('/api/polls/', defaults={"guild": None})
def api_polls(guild):
    return api("json_files/polls.json", guild)

@app.route('/api/levelroles/', defaults={"guild": None})
def api_lr(guild):
    return api("json_files/levelroles.json", guild)

@app.route('/api/prefixes/', defaults={"guild": None})
def api_prefixes(guild):
    return api("json_files/prefixes.json", guild)

@app.route("/leaderboard/", defaults={"guild": None})
@app.route("/lb/", defaults={"guild": None})
def leaderboard(guild):
    if not guild:
        guild = request.args.get("guild")
    if not guild:
        return "No guild id provided."
    else:
        with open("json_files/leveling.json", "r") as d:
            servers = json.load(d)
        if str(guild) in servers:
            data = servers[str(guild)]
        else:
            return "No data available for this guild."

        t = ranklist(data)

        # creates dict
        leaderboard = {}
        i = 0
        from extensions import leveling

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
        # creates html dataframe from dict
        html_data = pd.DataFrame.from_dict(leaderboard)
    return render_template(
        "leaderboard.html", guild=guild, guild_name=guild_name, data=leaderboard
    )


def run():
    app.run(host="0.0.0.0", port=random.randint(2000, 9000))


def keep_alive():
    from main import client

    global client
    server = Thread(target=run)
    server.start()