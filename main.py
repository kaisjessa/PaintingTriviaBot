import os
TOKEN = os.environ['token']
import discord
import re
import requests
import shutil
from fuzzywuzzy import fuzz
from painting import choose_painting, choose_painting2, choose_painting3
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
    #make_file()
    print("test")

  if(message.content.startswith('.help')):
    await message.channel.send('\n'.join(["Type **.start artist** *[optional startyear-endyear]* to receive a painting relating from that date range (e.g., '.artist 1850-1950')", "Then guess the artist to reveal the answer", "End your game with .end, check your score with .score", "More features coming..."]))

  if message.content.startswith('.start artist'):
    user_score = 0
    max_score = 0
    terminate = False
    while(not terminate):
      query = message.content[13:].replace(" ", "")
      artist, title, date, link = choose_painting3(query)
      name = str(title).replace(" ", "").lower()
      os.makedirs('./images/{}'.format(name))
      r = requests.get(link, stream=True)
      r.raw.decode_content = True
      filepath = './images/{}'.format(name) + '/' + name + '.jpeg'
      with open(filepath, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
        
      await message.channel.send("Name the artist of the following artwork:")
      await message.channel.send(file=discord.File(filepath))
      shutil.rmtree('./images/{}'.format(name))
  
      def my_check(message1):
        return message1.content.startswith(',')==False and message1.channel == message.channel and message1.author == message.author

      going = False
      while(not going):
        msg = await client.wait_for('message', check=my_check)
        if(msg.content.startswith('.end')):
          await msg.channel.send("**Artist:** {}\n**Title:** {}\n**Date:** {}".format(artist, title, date))
          await message.channel.send("Game over, your score: {}/{}".format(user_score, max_score))
          terminate = True
          going = True
        elif(msg.content.startswith('.score')):
          await message.channel.send("Your score: {}/{}".format(user_score, max_score))
        elif(msg.content.startswith('.')):
          print("")
        else:
          going = True

      if(not terminate):
        lastname = artist
        re.sub("[\(\[].*?[\)\]]", "", lastname)
        lastname = lastname.strip(" ").split(" ")[-1].lower()
        userlastname = msg.content.strip(" ").split(" ")[-1].lower()
        print(lastname, userlastname)
        print((fuzz.ratio(lastname, userlastname)))
        if(fuzz.ratio(lastname, userlastname) >= 60):
          await msg.channel.send("**Correct!**")
          user_score += 1
        else:
          await msg.channel.send("**Incorrect**")
        max_score += 1
        await msg.channel.send("**Artist:** {}\n**Title:** {}\n**Date:** {}".format(artist, title, date))
  
keep_alive()
client.run(TOKEN)