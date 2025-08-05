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
import asyncio

import time
import random
import shutil

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
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
folder_path = "/home/container/subdivs"
users = []
allcountries = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua_and_Barbuda",
    "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain",
    "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan",
    "Bolivia", "Bosnia_and_Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria",
    "Burkina_Faso", "Burundi", "Cabo_Verde", "Cambodia", "Cameroon", "Canada",
    "Central_African_Republic", "Chad", "Chile", "China", "Colombia", "Comoros",
    "Congo", "Costa_Rica", "Croatia", "Cuba", "Cyprus", "Czech_Republic_(Czechia)",
    "Democratic_Republic_of_the_Congo", "Denmark", "Djibouti", "Dominica", "Dominican_Republic",
    "Ecuador", "Egypt", "El_Salvador", "Equatorial_Guinea", "Eritrea", "Estonia", "Eswatini",
    "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana",
    "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti",
    "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland",
    "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati",
    "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya",
    "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia",
    "Maldives", "Mali", "Malta", "Marshall_Islands", "Mauritania", "Mauritius", "Mexico",
    "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique",
    "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New_Zealand",
    "Nicaragua", "Niger", "Nigeria", "North_Korea", "North_Macedonia", "Norway", "Oman",
    "Pakistan", "Palau", "Palestine", "Panama", "Papua_New_Guinea", "Paraguay", "Peru",
    "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda",
    "Saint_Kitts_and_Nevis", "Saint_Lucia", "Saint_Vincent_and_the_Grenadines", "Samoa",
    "San_Marino", "Sao_Tome_and_Principe", "Saudi_Arabia", "Senegal", "Serbia",
    "Seychelles", "Sierra_Leone", "Singapore", "Slovakia", "Slovenia", "Solomon_Islands",
    "Somalia", "South_Africa", "South_Korea", "South_Sudan", "Spain", "Sri_Lanka",
    "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Tajikistan", "Tanzania",
    "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad_and_Tobago", "Tunisia",
    "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United_Arab_Emirates",
    "United_Kingdom", "United_States", "USA", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican_City",
    "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe","Taiwan", "Kosovo"
]

domains = {
    "Afghanistan": "AF", "Albania": "AL", "Algeria": "DZ", "Andorra": "AD", "Angola": "AO",
    "Antigua and Barbuda": "AG", "Argentina": "AR", "Armenia": "AM", "Australia": "AU", "Austria": "AT",
    "Azerbaijan": "AZ", "Bahamas": "BS", "Bahrain": "BH", "Bangladesh": "BD", "Barbados": "BB",
    "Belarus": "BY", "Belgium": "BE", "Belize": "BZ", "Benin": "BJ", "Bhutan": "BT",
    "Bolivia": "BO", "Bosnia and Herzegovina": "BA", "Botswana": "BW", "Brazil": "BR", "Brunei": "BN",
    "Bulgaria": "BG", "Burkina Faso": "BF", "Burundi": "BI", "Cabo Verde": "CV", "Cambodia": "KH",
    "Cameroon": "CM", "Canada": "CA", "Central African Republic": "CF", "Chad": "TD", "Chile": "CL",
    "China": "CN", "Colombia": "CO", "Comoros": "KM", "Republic of the Congo": "CG", "Democratic Republic of the Congo": "CD",
    "Costa Rica": "CR", "Croatia": "HR", "Cuba": "CU", "Cyprus": "CY", "Czech Republic": "CZ",
    "Denmark": "DK", "Djibouti": "DJ", "Dominica": "DM", "Dominican Republic": "DO", "Ecuador": "EC",
    "Egypt": "EG", "El Salvador": "SV", "Equatorial Guinea": "GQ", "Eritrea": "ER", "Estonia": "EE",
    "Eswatini": "SZ", "Ethiopia": "ET", "Fiji": "FJ", "Finland": "FI", "France": "FR",
    "Gabon": "GA", "Gambia": "GM", "Georgia": "GE", "Germany": "DE", "Ghana": "GH",
    "Greece": "GR", "Grenada": "GD", "Guatemala": "GT", "Guinea": "GN", "Guinea-Bissau": "GW",
    "Guyana": "GY", "Haiti": "HT", "Honduras": "HN", "Hungary": "HU", "Iceland": "IS",
    "India": "IN", "Indonesia": "ID", "Iran": "IR", "Iraq": "IQ", "Ireland": "IE",
    "Israel": "IL", "Italy": "IT", "Ivory Coast": "CI", "Jamaica": "JM", "Japan": "JP",
    "Jordan": "JO", "Kazakhstan": "KZ", "Kenya": "KE", "Kiribati": "KI", "Kuwait": "KW",
    "Kyrgyzstan": "KG", "Laos": "LA", "Latvia": "LV", "Lebanon": "LB", "Lesotho": "LS",
    "Liberia": "LR", "Libya": "LY", "Liechtenstein": "LI", "Lithuania": "LT", "Luxembourg": "LU",
    "Madagascar": "MG", "Malawi": "MW", "Malaysia": "MY", "Maldives": "MV", "Mali": "ML",
    "Malta": "MT", "Marshall Islands": "MH", "Mauritania": "MR", "Mauritius": "MU", "Mexico": "MX",
    "Micronesia": "FM", "Moldova": "MD", "Monaco": "MC", "Mongolia": "MN", "Montenegro": "ME",
    "Morocco": "MA", "Mozambique": "MZ", "Myanmar": "MM", "Namibia": "NA", "Nauru": "NR",
    "Nepal": "NP", "Netherlands": "NL", "New Zealand": "NZ", "Nicaragua": "NI", "Niger": "NE",
    "Nigeria": "NG", "North Korea": "KP", "North Macedonia": "MK", "Norway": "NO", "Oman": "OM",
    "Pakistan": "PK", "Palau": "PW", "Palestine": "PS", "Panama": "PA", "Papua New Guinea": "PG",
    "Paraguay": "PY", "Peru": "PE", "Philippines": "PH", "Poland": "PL", "Portugal": "PT",
    "Qatar": "QA", "Romania": "RO", "Russia": "RU", "Rwanda": "RW", "Saint Kitts and Nevis": "KN",
    "Saint Lucia": "LC", "Saint Vincent and the Grenadines": "VC", "Samoa": "WS", "San Marino": "SM", "Sao Tome and Principe": "ST",
    "Saudi Arabia": "SA", "Senegal": "SN", "Serbia": "RS", "Seychelles": "SC", "Sierra Leone": "SL",
    "Singapore": "SG", "Slovakia": "SK", "Slovenia": "SI", "Solomon Islands": "SB", "Somalia": "SO",
    "South Africa": "ZA", "South Korea": "KR", "South Sudan": "SS", "Spain": "ES", "Sri Lanka": "LK",
    "Sudan": "SD", "Suriname": "SR", "Sweden": "SE", "Switzerland": "CH", "Syria": "SY",
    "Tajikistan": "TJ", "Tanzania": "TZ", "Thailand": "TH", "Timor-Leste": "TL", "Togo": "TG",
    "Tonga": "TO", "Trinidad and Tobago": "TT", "Tunisia": "TN", "Turkey": "TR", "Turkmenistan": "TM",
    "Tuvalu": "TV", "Uganda": "UG", "Ukraine": "UA", "United Arab Emirates": "AE", "United Kingdom": "GB",
    "United States": "US", "Uruguay": "UY", "Uzbekistan": "UZ", "Vanuatu": "VU", "Vatican City": "VA",
    "Venezuela": "VE", "Vietnam": "VN", "Yemen": "YE", "Zambia": "ZM", "Zimbabwe": "ZW"
}

continents = {
    "africa": [
        "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi",
        "Cabo Verde", "Cameroon", "Central African Republic", "Chad", "Comoros",
        "Democratic Republic of the Congo", "Republic of the Congo", "Djibouti",
        "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon",
        "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya",
        "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali", "Mauritania",
        "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", "Nigeria",
        "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles", "Sierra Leone",
        "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo",
        "Tunisia", "Uganda", "Zambia", "Zimbabwe"
    ],
    "asia": [
        "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan",
        "Brunei", "Cambodia", "China", "Cyprus", "Georgia", "India", "Indonesia",
        "Iran", "Iraq", "Israel", "Japan", "Jordan", "Kazakhstan", "Kuwait",
        "Kyrgyzstan", "Laos", "Lebanon", "Malaysia", "Maldives", "Mongolia",
        "Myanmar", "Nepal", "North Korea", "Oman", "Pakistan", "Palestine", "Philippines",
        "Qatar", "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka", "Syria",
        "Tajikistan", "Thailand", "Timor-Leste", "Turkey", "Turkmenistan", "United Arab Emirates",
        "Uzbekistan", "Vietnam", "Yemen"
    ],
    "europe": [
        "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus",
        "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus",
        "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Georgia",
        "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kazakhstan",
        "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta",
        "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway",
        "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia",
        "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Ukraine",
        "United Kingdom", "Vatican City"
    ],
    "north_america": [
        "Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Canada", "Costa Rica",
        "Cuba", "Dominica", "Dominican Republic", "El Salvador", "Grenada", "Guatemala",
        "Haiti", "Honduras", "Jamaica", "Mexico", "Nicaragua", "Panama",
        "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines",
        "Trinidad and Tobago", "United States"
    ],
    "south_america": [
        "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador",
        "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"
    ],
    "oceania": [
        "Australia", "Fiji", "Kiribati", "Marshall Islands", "Micronesia",
        "Nauru", "New Zealand", "Palau", "Papua New Guinea", "Samoa",
        "Solomon Islands", "Tonga", "Tuvalu", "Vanuatu"
    ]
}


@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

def genQuiz(country_name):
    if not os.path.isdir(folder_path+"/"+country_name):
        API_KEY = "API-KEY"
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

        with open(f"{folder_path}/usage.json", 'r', encoding='utf-8') as f:
            usage = json.load(f)

        if country_name not in usage:
            usage[country_name] = 1
        else:
            usage[country_name] += 1

        with open(f"{folder_path}/usage.json", "w") as f:
            json.dump(usage, f, indent=2)
            
        json_path = os.path.join(output_folder, "subdivs.json")
        with open(json_path, "w") as f:
            json.dump(mapping, f, indent=2)

def get_folder_size(path):
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)  # Convert to MB

def load_usage_data(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_total_subdivs_size(folder_path, exclude_folders):
    total = 0
    for name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, name)
        if os.path.isdir(full_path) and name not in exclude_folders:
            total += get_folder_size(full_path)
    return total

def delete_worst_subdivs(folder_path, max_size_mb=500):
    usage_path = os.path.join(folder_path, "usage.json")
    usage_data = load_usage_data(usage_path)

    exclude = {"leaderboard", "usage.json"}
    folder_scores = []

    for name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, name)
        if os.path.isdir(full_path) and name not in exclude:
            size_mb = get_folder_size(full_path)
            usage = usage_data.get(name, 0)
            score = size_mb - (usage * 10)
            folder_scores.append((name, full_path, size_mb, usage, score))

    # Sort from worst (highest score) to best
    folder_scores.sort(key=lambda x: x[-1], reverse=True)

    # Delete worst until under size
    current_size = get_total_subdivs_size(folder_path, exclude)

    for name, path, size_mb, usage, score in folder_scores:
        if current_size <= max_size_mb:
            break
        #print(f"Deleting: {name} | Size: {size_mb:.2f} MB | Usage: {usage} | Score: {score:.2f}")
        shutil.rmtree(path)
        current_size -= size_mb   
    
@bot.command()
async def alias(ctx, name: str):
    try:
        name = name.title()
        await ctx.send("Generating Quiz Data...")
        genQuiz(name)
        with open(f"{folder_path}/{name}/subdivs.json", 'r', encoding='utf-8') as f:
            subdivs = json.load(f)
            await ctx.send("\n".join(f"{i+1}. {v}" for i, v in enumerate(subdivs.values())))
        delete_worst_subdivs(folder_path, max_size_mb=500)
    except:
        await ctx.send("Invalid Country!")

async def start(ctx, quiz, name, quizType, messageType):
    if ctx.author in users:
        await ctx.send("You already have an active quiz!")
        return
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    users.append(ctx.author)
    start = time.time()
    bonus = 0
    skips = 0
    keys = list(quiz.keys())
    random.shuffle(keys)
    for i, key in enumerate(keys):
        if messageType == "file":
          await ctx.send(f"{i+1}/{len(quiz)}",file=discord.File(key.replace("/Users/RishiK/Desktop/subdivs",folder_path)))
        elif messageType == "embed":
          embed = discord.Embed()
          embed.set_image(url=key)
          await ctx.send(f"{i+1}/{len(keys)}",embed=embed)
        else:
          await ctx.send(f"{i+1}/{len(keys)}: {key}")
        correct = False

        while not correct:
            try:
              response = await bot.wait_for('message', check=check, timeout = 60)
            except asyncio.TimeoutError:
              await ctx.send("You took too long to respond! Quiz ended")
              return
            answer = response.content.lower()
            if answer in quiz[key]:
                await response.add_reaction("✅")
                correct = True
            elif answer == "skip":
                bonus += 30
                await response.add_reaction("✅")
                skips += 1
                answers = "\n".join(list(quiz[key]))
                await ctx.send(f"Possible Answers:\n{answers}")
                correct = True
            elif answer == "stop":
                users.remove(ctx.author)
                await ctx.send("Quiz Stopped")
                delete_worst_subdivs(folder_path, max_size_mb=500)
                return
            else:
                await response.add_reaction("❌")
    end = time.time()
    runtime = round(end-start+bonus,2)
    users.remove(ctx.author)
    user_name = str(ctx.author.id)
    if quizType != "quiz":
      name = quizType+"_"+name
    await ctx.send(f"Quiz finished! Final time: {runtime} {skips}/{len(keys)} Skipped")
    delete_worst_subdivs(folder_path, max_size_mb=500)
    if skips == len(keys):
      await ctx.send("Everything skipped, time not applicable for a record!")
      return
    for i in range(2):
      if i == 0:
        lbname = "endless"
      elif i == 1:
        if name not in allcountries:
          break
        lbname = "country"
      with open(f"{folder_path}/{lbname}leaderboard.json", 'r', encoding='utf-8') as f:
        leaderboard = json.load(f)
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
        with open(f"{folder_path}/{lbname}leaderboard.json", "w", encoding="utf-8") as f:
          json.dump(leaderboard, f, indent=2)
        await ctx.send(f"New {lbname.title()} Record!")

  
    
@bot.command()
async def quiz(ctx, name: str):
    try:
        name = name.title()
        await ctx.send("Generating Quiz Data...")
        genQuiz(name)
        with open(f"{folder_path}/{name}/subdivs.json", 'r', encoding='utf-8') as f:
            subdivs = json.load(f)
        await ctx.send("Starting the quiz!")       
    except:
        await ctx.send("Invalid Country!")
        return
    await start(ctx, subdivs, name, "subdivs", "file")
    

@bot.command()
async def flags(ctx, continent: str):
  continent = continent.lower()
  if continent == "world":
    keys = list(domains.keys())
  elif continent in continents:
    keys = continents[continent]
  else:
    await ctx.send("Invalid continent!")
    return
  quiz = {}
  for key in keys:
    quiz[f"https://flagsapi.com/{domains[key]}/flat/64.png"] = [key.lower()]
  await start(ctx, quiz, continent, "flags", "embed")

@bot.command()
async def whatdomain(ctx, continent: str):
  continent = continent.lower()
  if continent == "world":
    keys = list(domains.keys())
  elif continent in continents:
    keys = continents[continent]
  else:
    await ctx.send("Invalid continent!")
    return
  quiz = {}
  for key in keys:
    if key == "United Kingdom":
      quiz[key] = ["uk"] 
    else:
      quiz[key] = [domains[key].lower()] 
  await start(ctx, quiz, continent, "whatdomain", "text")

@bot.command()
async def domain(ctx, continent: str):
  continent = continent.lower()
  if continent == "world":
    keys = list(domains.keys())
  elif continent in continents:
    keys = continents[continent]
  else:
    await ctx.send("Invalid continent!")
    return
  quiz = {}
  for key in keys:
    if key == "United Kingdom":
      quiz["uk"] = [key.lower()] 
    else:
      quiz[domains[key].lower()] = [key.lower()] 
  await start(ctx, quiz, continent, "domain", "text")
  
@bot.command()
async def leaderboard(ctx, lbname: str):
    with open(f"{folder_path}/{lbname}leaderboard.json", 'r', encoding='utf-8') as f:
        leaderboard = json.load(f)

    # Sort users by number of records (descending)
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: len(x[1]), reverse=True)

    header = "🏆 **Leaderboard**\n"
    message_chunks = []
    current_chunk = "```"
    topusers = []
    tied = []
    i = 0
    members = [member async for member in ctx.guild.fetch_members(limit=None)]
    for user, records in sorted_leaderboard:
        inserver = False
        if len(records) == 0:
            continue
        if i == 0:
          toprecord = len(records)
          tied.append(user)
        elif i > 0:
          if len(records) == toprecord:
            tied.append(user)
          else:
            toprecord = len(records)
            topusers.append(tied)
            tied = [user]
        for member in members:
          if member.id == int(user):
            inserver = True
            break
        if inserver:
          user_line = f"{member.name} ({len(records)}):\n"
        else:
          user_line = f"{user} ({len(records)}):\n"
        if len(current_chunk) + len(user_line) >= 1990:
            current_chunk += "```"
            message_chunks.append(current_chunk)
            current_chunk = "```"

        current_chunk += user_line

        for quiz, time in sorted(records.items(), key=lambda x: x[0]):
            line = f"  - {quiz}: {float(time):.2f} sec\n"
            if len(current_chunk) + len(line) >= 1990:
                current_chunk += "```"
                message_chunks.append(current_chunk)
                current_chunk = "```"
            current_chunk += line

        current_chunk += "\n"  # add spacing between users
        i += 1
    topusers.append(tied)
    # Add the final chunk
    if current_chunk.strip("``` \n"):
        current_chunk += "```"
        message_chunks.append(current_chunk)

    # Send the messages
    await ctx.send(header)
    for chunk in message_chunks:
        await ctx.send(chunk)

    with open(folder_path+"/roles.json","r") as f:
      roles = json.load(f)
    if str(ctx.guild.id) not in roles:
      return
      
    memberAdded = False
    role = ctx.guild.get_role(roles[str(ctx.guild.id)])
    for member in members:
      if role in member.roles:
        await member.remove_roles(role)
    for tied in topusers:
      for user in tied:
        for member in members:
          if member.id == int(user):
            break
        if member:
          await member.add_roles(role)
          memberAdded = True
      if memberAdded == True:
        break
      
@bot.command()
async def record(ctx, name: str):
    with open(f"{folder_path}/endlessleaderboard.json", 'r', encoding='utf-8') as f:
        leaderboard = json.load(f)
    for user in leaderboard:
        for quiz in leaderboard[user]:
            if quiz.lower() == name.lower():
              members = [member async for member in ctx.guild.fetch_members(limit=None)]
              username = user
              for member in members:
                if member.id == int(user):
                  username = ctx.guild.get_member(int(user)).name
                  break
              await ctx.send(f"{username}'s Record: {leaderboard[user][quiz]}")
              return
    await ctx.send("Record Not Found")

@bot.command()
async def setWinnerRole(ctx, roleid: int):
  if not ctx.author.guild_permissions.administrator:
    await ctx.send("You do not have perms to run this command!")
    return
  role = ctx.guild.get_role(roleid)
  if role is None:
    await ctx.send("Role not found")
    return
  with open(folder_path+"/roles.json","r") as f:
    roles = json.load(f)
  roles[str(ctx.guild.id)] = roleid
  with open(folder_path+"/roles.json","w") as f:
    json.dump(roles,f,indent=2)
  await ctx.send(f"{role.name} set as the quiz record holder role")
    
# Replace 'token' with your actual bot token
bot.run('BOT-TOKEN')
