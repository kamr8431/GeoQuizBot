import ssl
import certifi
import discord
from discord.ext import commands
import aiohttp.connector

from googletrans import Translator
import requests
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import shape
import os
import json
import unicodedata

import time
import random

# Patch aiohttp TCPConnector to use certifi certs for SSL verification
original_init = aiohttp.connector.TCPConnector.__init__

def new_init(self, *args, **kwargs):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    kwargs['ssl'] = ssl_context
    original_init(self, *args, **kwargs)

aiohttp.connector.TCPConnector.__init__ = new_init

# Initialize the bot with a command prefix and intents
intents = discord.Intents.default()
intents.message_content = True # Enable message content intent
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

def genQuiz(country_name):
    folder_path = "/Users/RishiK/Desktop/subdivs"

    if not os.path.isdir(folder_path+"/"+country_name):
        API_KEY = "2dfa7616b7fa497a97f4f6425f510962"

        translator = Translator()
        # --- Step 1: Get Switzerland place_id
        geocode_url = "https://api.geoapify.com/v1/geocode/search"
        geocode_params = {
            "text": country_name,
            "apiKey": API_KEY
        }
        geocode_resp = requests.get(geocode_url, params=geocode_params)
        geocode_resp.raise_for_status()
        swiss_place_id = geocode_resp.json()["features"][0]["properties"]["place_id"]

        # --- Step 2: Get subdivisions
        boundaries_url = "https://api.geoapify.com/v1/boundaries/consists-of"
        boundaries_params = {
            "apiKey": API_KEY,
            "id": swiss_place_id,
            "boundary": "administrative",
            "sublevel": 1,
            "geometry": "geometry_1000",
            "lang": "en"
        }
        boundaries_resp = requests.get(boundaries_url, params=boundaries_params)
        boundaries_resp.raise_for_status()
        features = boundaries_resp.json()["features"]

        # --- Step 3: Convert to GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(features)
        # --- Step 4: Create output folder
        output_folder = f"{folder_path}/{country_name}"
        os.makedirs(output_folder, exist_ok=True)

        # --- Step 5: Generate individual images
        mapping = {}

        for idx, row in gdf.iterrows():
            name = row.get("name", f"subdiv_{idx}")
            filename = f"{name.replace(' ', '_').replace('/', '-')}.png"
            filepath = os.path.join(output_folder, filename)

            # Plot setup
            fig, ax = plt.subplots(figsize=(6, 6))
            gdf.boundary.plot(ax=ax, color="black", linewidth=1)
            gpd.GeoSeries(row.geometry).plot(ax=ax, color="red")

            plt.axis("off")
            plt.tight_layout()
            plt.savefig(filepath, dpi=150)
            plt.close()

            # Add to dictionary
            name = name.lower()
            namelist = name.split('/')
            for n in namelist:
                name = name.replace('-',' ')
                name = name.replace('_',' ')
                if not all(('a' <= c <= 'z') or c.isspace() for c in name):
                    name = translator.translate(n, src='auto', dest='en').text.lower()
                name = ''.join(
                c for c in unicodedata.normalize('NFKD', name)
                if not unicodedata.combining(c))
                name = name.replace('region','').strip()
                name = ''.join(char for char in name if char.isalnum() or char == ' ')
                if n != name:
                    namelist.append(name)
            mapping[filepath] = namelist

        if len(namelist)==0:
            os.rmdir(output_folder)
            raise ValueError("No subdivisions found!")
        # --- Step 6: Save JSON dictionary
        json_path = os.path.join(output_folder, "subdivs.json")
        with open(json_path, "w") as f:
            json.dump(mapping, f, indent=2)

@bot.command()
async def alias(ctx, name: str):
    try:
        name = name.title()
        await ctx.send("Generating Quiz Data...")
        genQuiz(name)
        with open(f"/Users/RishiK/Desktop/subdivs/{name}/subdivs.json", 'r', encoding='utf-8') as f:
            subdivs = json.load(f)
            await ctx.send("\n".join(f"{i+1}. {v}" for i, v in enumerate(subdivs.values())))
    except:
        await ctx.send("Invalid Country!")
    
@bot.command()
async def quiz(ctx, name: str):
    try:
        name = name.title()
        await ctx.send("Generating Quiz Data...")
        genQuiz(name)
        with open(f"/Users/RishiK/Desktop/subdivs/{name}/subdivs.json", 'r', encoding='utf-8') as f:
            subdivs = json.load(f)
        keys = list(subdivs.keys())
        random.shuffle(keys)   
        await ctx.send("Starting the quiz!")       
    except:
        await ctx.send("Invalid Country!")
        return
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    start = time.time()
    bonus = 0
    for i, key in enumerate(keys):
        await ctx.send(f"{i+1}/{len(subdivs)}",file=discord.File(key))
        correct = False

        while not correct:
            response = await bot.wait_for('message', check=check)
            answer = response.content
            if answer.lower() in subdivs[key]:
                await response.add_reaction("✅")
                correct = True
            elif answer == "skip":
                bonus += 30
                await response.add_reaction("✅")
                answers = "\n".join(subdivs[key])
                await ctx.send(f"Possible Answers:\n{answers}")
                correct = True
            elif answer == "stop":
                await ctx.send("Quiz Stopped")
                return
            else:
                await response.add_reaction("❌")
    end = time.time()
    runtime = round(end-start+bonus,2)
    await ctx.send(f"Quiz finished! Final time: {runtime}")

    with open("/Users/RishiK/Desktop/subdivs/leaderboard.json", 'r', encoding='utf-8') as f:
        leaderboard = json.load(f)

    user_name = ctx.author.name
    record = True
    for user in leaderboard:
        if name in leaderboard[user]:
            #print(leaderboard[user][name])
            if leaderboard[user][name] <= runtime:
                record = False
            else:
                del leaderboard[user][name]
            break

    if record:
        if user_name not in leaderboard:
            leaderboard[user_name] = {}
        leaderboard[user_name][name] = runtime
        await ctx.send("New Record!")
        with open("/Users/RishiK/Desktop/subdivs/leaderboard.json", "w", encoding="utf-8") as f:
            json.dump(leaderboard, f, indent=2)

@bot.command()
async def leaderboard(ctx):
    import json

    with open("/Users/RishiK/Desktop/subdivs/leaderboard.json", 'r', encoding='utf-8') as f:
        leaderboard = json.load(f)

    # Sort users by number of records (descending)
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: len(x[1]), reverse=True)

    lines = ["🏆 **Leaderboard**\n", "```"]

    for user, records in sorted_leaderboard:
        lines.append(f"{user} ({len(records)}):")
        for quiz, time in sorted(records.items(), key=lambda x: x[0]):
            lines.append(f"  - {quiz}: {float(time):.2f} sec")
        lines.append("")  # blank line between users

    lines.append("```")

    message = "\n".join(lines)
    await ctx.send(message)

    
# Replace 'token' with your actual bot token
bot.run('BOT_TOKEN')
