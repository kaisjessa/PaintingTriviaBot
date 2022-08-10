import os
TOKEN = os.environ['token']
import discord
import re
from fuzzywuzzy import fuzz
from painting import choose_painting, choose_painting2
from keep_alive import keep_alive
from web_scraper import make_file

client = discord.Client()

@client.event
async def on_ready():
  print("Logged in as {0.user}".format(client))
  #make_file()

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if(message.content.startswith('.test')):
    choose_painting3()

  if(message.content.startswith('.help')):
    await message.channel.send('\n'.join(["Type **.artist** *[optional startyear-endyear]* to receive a painting relating from that date range (e.g., '.artist 1850-1950')", "Then guess the artist to reveal the answer", "More features coming..."]))

  if message.content.startswith('.artist'):
    query = message.content[8:].replace(" ", "")
    artist, title, date, link = choose_painting3(query)
    await message.channel.send("Name the artist of the following painting:")
    await message.channel.send(link)
    await message.channel.send("Type anything to reveal the answer")

    def my_check(message1):
      return message1.content.startswith(',')==False and message1.channel == message.channel and message1.author == message.author
      
    msg = await client.wait_for('message', check=my_check)
    lastname = artist
    re.sub("[\(\[].*?[\)\]]", "", lastname)
    lastname = lastname.strip(" ").split(" ")[0].lower()
    userlastname = msg.content.strip(" ").split(" ")[-1].lower()
    print(lastname, userlastname)
    print((fuzz.ratio(lastname, userlastname)))
    if(fuzz.ratio(lastname, userlastname) >= 60):
      await msg.channel.send("**Correct!**")
    else:
      await msg.channel.send("**Incorrect**")
    await msg.channel.send("**Artist:** {}\n**Title:** {}\n**Date:** {}".format(artist, title, date))
  
keep_alive()
client.run(TOKEN)