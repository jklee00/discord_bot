# To run, go to bot directory
# activate virtual environment using activate.bat in the -env directory
# windows: bot-env\Scripts\activate.bat
# to deactivate, just use: deactivate
# activate.bat has CLRF line terminators (windows), to use in Unix you must convert to Unix line endings
import discord
from discord.ext import commands
import logging
import logging.handlers
import random
import requests
import json

#Todo
#import youtube_dl
#from music import music_cog

# Outputs debug output for library outputs (does not do HTTP requests)
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

#Set the default prefix for commands
DEFAULT_PREFIX = '!'

#Get the bot setup for usage
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=DEFAULT_PREFIX, intents=intents)
#bot.add_cog(music_cog(bot))


#Create Events & Commands

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}! (ID: {bot.user.id})')
    print('--------------')

#@bot.event
#async def on_member_join():

# This would put messages sent in server to output
#@bot.event
#async def on_message(bot.user, message):
#    print(f'Message from {message.author}: {message.content}')

# Member Join
@bot.command(name="join", description="Shows when a user joined server", help="Shows when a user joined server")
async def join(ctx, member: discord.Member = commands.parameter(description="The user you want to check")):
    await ctx.send(f'{member.name} joined {discord.utils.format_dt(member.joined_at)}')
@join.error
async def calc_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Proper usage: !join {username}')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Proper usage: !join {username}')

# Latency command
# !ping
@bot.command(name="ping", description="Shows user latency", help="Shows user latency")
async def ping(ctx: commands.Context):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

# Basic calculator command
# !calc {expression}
@bot.command(name="calc", description="Do a basic calculation", help="Do a basic calculation")
async def calc(ctx, *, args = commands.parameter(description="A basic calculation (+, -, /, *, etc)")):
    calculation = eval(args)
    await ctx.send('Your question: {}\nAnswer: {}'.format(args, calculation))
# Account for possible user errors: missing args
@calc.error
async def calc_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Proper usage: !calc {expression}')

# Random number generator
@bot.command(name="rand", description="Provides a random number between 0 and a specified number", help="Random positive number generator")
async def rand(ctx, num:int = commands.parameter(description="A whole number greater than 0")):
    await ctx.send(random.randrange(num))
@rand.error
async def rand_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Proper usage: !rand {number}')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Proper usage: !rand {number}')
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send('Number must be a natural number')


#Riot API commands

TOKEN_RIOT = "Riot API key goes here"

#Helper functions
def getName(nameWithSpaces):
    result = ""
    for n in nameWithSpaces:
        result = result + " " + str(n)
    return result

#Get LOL name, level, icon, and ID
def lolProfile(name):
    API_Riot = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key=" + TOKEN_RIOT
    response = requests.get(API_Riot)
    jsonDataSummoner = response.json()
    sName = jsonDataSummoner['name']
    sLevel = "Lvl. " + str(jsonDataSummoner['summonerLevel'])
    sIcon = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/profileicon/" + str(jsonDataSummoner['profileIconId']) + ".png"
    sEncryptedID = jsonDataSummoner['id']
    return (sName, sLevel, sIcon, sEncryptedID)

#Get LOL/TFT ranked information
def lolRank(sEncryptedID):
    API_Riot = "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + sEncryptedID + "?api_key=" + TOKEN_RIOT
    API_Riot_TFT = "https://na1.api.riotgames.com/tft/league/v1/entries/by-summoner/" + sEncryptedID + "?api_key=" + TOKEN_RIOT
    response = requests.get(API_Riot)
    jsonDataSummoner = response.json()
    calls = {0:"queueType", 1:"tier", 2:"rank", 3:"leaguePoints", 4:"wins", 5:"losses"}
    ranks = []
    try:
        for i in range(3):
            for j in range(6):
                ranks.append(jsonDataSummoner[i][calls[j]])
    except:
        pass
    response = requests.get(API_Riot_TFT)
    jsonDataSummoner = response.json()
    calls = {0:"queueType", 1:"tier", 2:"rank", 3:"leaguePoints", 4:"wins", 5:"losses"}
    try:
        for i in range(3):
            for j in range(6):
                ranks.append(jsonDataSummoner[i][calls[j]])
    except:
        pass
    return ranks

''' todo
#Get status of LOL/TFT/VAL
def status(game):
    if game == "lol":
        API_Riot = "https://na1.api.riotgames.com/lol/status/v4/platform-data" + "?api_key=" + TOKEN_RIOT
        response = requests.get(API_Riot)
        jsonStatus = response.json()
        calls = {0:"id", 1:"name", 2:"maintenences", 3:"incidents"}
        currstatus = []
        try:
            for i in range(4):
                status.append(jsonStatus[0][calls[i]])
        except:
            pass

        return currstatus
    elif game == "tft":
        API_Riot_TFT = "https://na1.api.riotgames.com/tft/status/v1/platform-data/" + "?api_key=" + TOKEN_RIOT
        response = requests.get(API_Riot_TFT)
        jsonStatus = response.json()
        calls = {0:"id", 1:"name", 2:"maintenences", 3:"incidents"}
        currstatus = []
        try:
            for i in range(4):
                status.append(jsonStatus[0][calls[i]])
        except:
            pass

        return currstatus
    elif game == "val":
        API_Riot_VAL = "https://na1.api.riotgames.com/val/status/v1/platform-data" + "?api_key=" + TOKEN_RIOT
        response = requests.get(API_Riot_VAL)
        jsonStatus = response.json()
        calls = {0:"id", 1:"name", 2:"maintenences", 3:"incidents"}
        currstatus = []
        try:
            for i in range(4):
                status.append(jsonStatus[0][calls[i]])
        except:
            pass

        return currstatus
    
    else:
        return 0
'''


@bot.command(name="lol", description="Shows a League of Legends player on the NA server, including their username, profile picture, level, and ranks", help="Shows a Lol user and their ranks")
async def lol(ctx, *username):
    name = getName(username)
    summoner = lolProfile(name)
    summonerRanking = lolRank(summoner[3])
    embed = discord.Embed(title=summoner[0], description=summoner[1], color=0x8E7CC3)
    embed.set_thumbnail(url=summoner[2])
    
    # Check LOL/TFT Ranks
    # For TFT, wins = first placement, losses = 2nd - 8th
    try:
        tmp = f"{summonerRanking[1]} {summonerRanking[2]} • LP:{summonerRanking[3]} • Wins: {summonerRanking[4]} • Losses: {summonerRanking[5]}"
        embed.add_field(name=summonerRanking[0], value=tmp, inline=False)
    except:
        embed.add_field(name="Not found", value="Player hasn't any ranked status.", inline=False)
   
    try:
        tmp = f"{summonerRanking[7]} {summonerRanking[8]} • LP:{summonerRanking[9]} • Wins: {summonerRanking[10]} • Losses: {summonerRanking[11]}"
        embed.add_field(name=summonerRanking[6], value=tmp, inline=False)
    except:
        pass
    
    try:
        tmp = f"{summonerRanking[13]} {summonerRanking[14]} • LP:{summonerRanking[15]} • Wins: {summonerRanking[16]} • Losses: {summonerRanking[17]}"
        embed.add_field(name=summonerRanking[12], value=tmp, inline=False)
    except:
        pass

    await ctx.send(embed=embed)
@lol.error
async def lol_error(ctx, error):
    if isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send('Proper usage: !lol {Summoner Name}')

''' todo
@bot.command()
async def status(ctx, game):
#ctx: commands.Context
    currstatus = status(game)
    if currstatus == 0:
        await ctx.send("Proper usage: !status {lol/tft/val}")
    embed = discord.Embed(title="Status")
    try:
        tmp = f"{currstatus[1]}"
        embed.add_field(name="Test", value=tmp, inline=False)
    except:
        embed.add_field(name="Failure", value="Failure", inline=False)

    await ctx.send(embed=embed)
@status.error
async def status_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('Proper usage: !status {lol/tft/val}')
'''

#Token
bot.run('Discord bot token goes here')