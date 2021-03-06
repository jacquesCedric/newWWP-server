# WWP Bot

import os
import os.path
from os import path
import requests
from datetime import datetime
from xml.sax.saxutils import escape, unescape

import discord
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
listener = os.getenv('LISTENER_URL')
fileserver = os.getenv('FILESERVER_URL')

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

# bot = commands.Bot(command_prefix='!')
bot = commands.Bot(
    command_prefix = '!',
    description = 'I help to search and vote for Wii U titles',
    help_command = help_command
)

@bot.command(name="search", help="Search for ids by title")
async def searchForTitle(ctx, term):
    results = searchByTitle(term)
    if len(results) == 0:
        embed=discord.Embed(title="No titles found", description="Sorry, no titles found containing: \"" + term + "\"")
        await ctx.send(embed=embed)
    else:
        embed=discord.Embed(title="Search results for: \"" + term + "\"", description=formatSearchResults(results) )
        await ctx.send(embed=embed)


@bot.command(name="vote", help="Vote for a title using its id")
async def voteForTitle(ctx, titleID):
    d = detailsFromID(titleID)

    if d == 0:
        embed=discord.Embed(title="Vote failed", description="Sorry, I don't recognize \"" + titleID + "\" as a title ID\rTry using the \"!search\" command to find the correct ID")
        await ctx.send(embed=embed)
    else:
        s = d.split(';')

        embed=discord.Embed(title="Added vote for \"" + s[1] + "\"", description="[" + s[2].upper().rstrip() + "] - " + s[0])

        if (path.exists("/resources/images/pngs/" + titleID + ".png")):
            sendVoteToServer(titleID)
            file = discord.File("/resources/images/pngs/" + titleID + ".png", filename="image.png")
            embed.set_thumbnail(url="attachment://image.png")
            await ctx.send(file=file, embed=embed)

        else:
            await ctx.send(embed=embed)

# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, discord.ext.commands.errors.CommandNotFound):
#         await ctx.send("That command wasn't found!")        

@bot.event
async def on_message(message):
    if not message.content:
        return
    elif message.author == bot.user:
        return
    elif message.content[0] == "!" :
        await bot.process_commands(message)
    elif message.content.strip() != "":
        ts = message.created_at
        st = ts.strftime('%Y-%m-%d %H:%M:%S')

        sanit = escape(unescape(message.content[:100].strip().strip(";;")))
        saname = escape(unescape(message.author.name[:20].strip().strip(";;")))
        sendChatToServer(saname, st, sanit)


# helper functions
# Vote functions
# Write titleID to file for vote tallying
def sendVoteToServer(titleID):
    data = {"type": "vote", "titleID": titleID}
    try:
        response = requests.post(listener, data)
        print(response)
    except Exception as e:
        handleException(e)

def sendChatToServer(author, time, msg):
    data = {"type": "chat", "author": author, "time": time, "message": msg}
    try:
        response = requests.post(listener, data)
        print(response)
    except Exception as e:
        handleException(e)
    


# Printing functions
def formattedStringfromResult(result):
    s = result.rstrip().split(';')
    f = "\"" + s[1] + "\" [" + s[2].upper() + "] - " + s[0]
    return f

def formatSearchResults(results):
    s = []
    for r in results:
        s.append(formattedStringfromResult(r))

    return "\n".join(s)


# Searching functions
def searchByTitle(term):
    results = []

    try: 
        r = requests.get(fileserver + "/text/titleinfo.txt")
        r.encoding = "utf-8"
        
        for line in r.text.splitlines():
            if term.upper() in line.upper():
                results.append(line)
            if len(results) > 5 :
                return results
    except Exception as e:
        handleException(e)
        return results

    return results


def detailsFromID(titleID):
    try: 
        r = requests.get(fileserver + "/text/titleinfo.txt")
        r.encoding = "utf-8"
        for line in r.text.splitlines():
            if line[8:16] == titleID[8:16]:
                return line
    except Exception as e:
        handleException(e)
    
    return 0

def titleFromID(titleID):
    d = detailsFromID(titleID)
    s = d.split(';')
    return s[1]

# Housekeeping
def handleException(e):
    print("There was an issue:")
    if (e.message):
        print(e.message)
        


bot.run(TOKEN)