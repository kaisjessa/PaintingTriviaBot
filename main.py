# imports
import os
TOKEN = os.environ['token']
import discord
import re
import requests
import shutil
import asyncio
import time
from fuzzywuzzy import fuzz
from painting import choose_painting3, cropper

active_channels = []
developer_id = int(os.environ['developer_id'])
artist_dict = {True: "Artist", False: "Title"}
easy_dict = {0: "Easy", 1: "Hard", 2: "Extreme"}

# determines if an image url is valid
def is_valid(url):
  try:
    res = requests.get(url)
    return res.ok
  except:
    return False

def choose_painting(message, easy, query):
  try:
    worked = False
    while(not worked):
      # get a working painting link
      # save it to its own folder
      artist, title, date, link = choose_painting3(easy, query)
      filepath = ""
      # try: 
      #print(link)
      while(not is_valid(link)):
        #print(link)
        artist, title, date, link = choose_painting3(easy, query)
      name = str(title).split(" / ")[0].replace(" ", "").lower()
      os.makedirs('./images/{}/{}'.format(message.channel.id, name))
      r = requests.get(link, stream=True)
      r.raw.decode_content = True
      suffix = '.jpg'
      if(link.endswith('.jpeg')):
        suffix = '.jpeg'
      elif(link.endswith('.png')):
        suffix = '.png'
      filepath = './images/{}/{}'.format(message.channel.id, name) + '/' + "image" + suffix
      with open(filepath, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
      worked = True
  except:
    with open("errors.log", "a") as f:
      f.write("{} did not work".format(link))
    print("{} did not work".format(link))
    worked = False
  return artist, title, date, link, filepath

# uncropped game
async def uncropped_game(message, use_artist, easy, query):
  # add channel to active channels
  active_channels.append(message.channel.id)
  await message.channel.send('Starting your game...')
  user_score = 0
  max_score = 0
  terminate = False
  while(not terminate):
    artist, title, date, link, filepath = choose_painting(message, easy, query)
    if(use_artist):
      print("{}: {}".format(message.author.name, artist))
    else:
      print("{}: {}".format(message.author.name, title))

    def my_check(message1):
      return message1.content.startswith(',')==False and message1.channel == message.channel and message1.author == message.author

    try:
        if(use_artist):
          await message.channel.send("Name the artist of the following artwork:")
        else:
          await message.channel.send("Give the title of the following artwork:")
        # send image and then delete the file
        await message.channel.send(file=discord.File(filepath))
        shutil.rmtree('./images/{}'.format(message.channel.id))
    except:
      await message.channel.send("Sorry! Something went wrong :(")
    going = False
    while(not going):
      try:
        # check for user messages
        # timeout after 10 mins
        msg = await client.wait_for('message', check=my_check, timeout = 600)
        if(msg.content.startswith('.end')):
          answer_embed = discord.Embed(title="")
          answer_embed.add_field(name="Artist", value=artist, inline=True)
          answer_embed.add_field(name = "Title", value=title, inline=True)
          answer_embed.add_field(name = "Date", value=date, inline=True)
          await message.channel.send(embed=answer_embed)
          
          game_over_embed = discord.Embed(title="Game Over!")
          game_over_embed.add_field(name="Your score:", value = "{}/{}".format(user_score, max_score))
          await message.channel.send(embed=game_over_embed)
          terminate = True
          going = True
          active_channels.remove(message.channel.id)
        elif(msg.content.startswith('.score')):
          game_over_embed = discord.Embed(title="Score")
          game_over_embed.add_field(name="Your score:", value = "{}/{}".format(user_score, max_score))
          await message.channel.send(embed=game_over_embed)
        elif(msg.content.startswith('.')):
          print("")
        else:
          print("{} guessed: {}".format(msg.author.name, msg.content))
          going = True
      except asyncio.TimeoutError:
        await message.channel.send("Your game has timed out")
        answer_embed = discord.Embed(title="")
        answer_embed.add_field(name="Artist", value=artist, inline=True)
        answer_embed.add_field(name = "Title", value=title, inline=True)
        answer_embed.add_field(name = "Date", value=date, inline=True)
        await message.channel.send(embed=answer_embed)
        game_over_embed = discord.Embed(title="Game Over!")
        game_over_embed.add_field(name="Your score:", value = "{}/{}".format(user_score, max_score))
        await message.channel.send(embed=game_over_embed)
        terminate = True
        going = True
        active_channels.remove(message.channel.id)
        

    # compare user answer to correct
    if(not terminate):
      if(use_artist):
        answers = artist
        re.sub("[\(\[].*?[\)\]]", "", answers)
        answers = answers.lower().strip(" ").split(" ")
        user_answers = msg.content.lower().strip(" ").split(" ")
      else:
        answers = [x.strip(" ") for x in title.lower().split("/")]
        user_answers = [msg.content.lower().strip(" ")]
      found = False
      for answer in answers:
        for user_answer in user_answers:
          if(fuzz.ratio(user_answer, answer) >= 65):
            found = True
      if(found):
        await msg.channel.send("**Correct!**")
        user_score += 1
      else:
        await msg.channel.send("**Incorrect**")
      max_score += 1
      answer_embed = discord.Embed(title="")
      answer_embed.add_field(name="Artist", value=artist, inline=True)
      answer_embed.add_field(name = "Title", value=title, inline=True)
      answer_embed.add_field(name = "Date", value=date, inline=True)
      await message.channel.send(embed=answer_embed)
      await msg.channel.send("Loading next artwork, commands not accepted during this time...")

async def cropped_game(message, use_artist, easy, query):
  active_channels.append(message.channel.id)
  await message.channel.send('Starting your game...')
  user_score = 0
  user_scores = [0, 0, 0, 0, 0, 0]
  max_score = 0
  terminate = False
  while(not terminate):
    artist, title, date, link, filepath = choose_painting(message, easy, query)
    print(artist, title, date, link, filepath)
    if(use_artist):
      print("{}: {}".format(message.author.name, artist))
    else:
      print("{}: {}".format(message.author.name, title))
    if(use_artist):
      await message.channel.send("Name the artist of the following artwork:")
    else:
      await message.channel.send("Give the title of the following artwork:")

    def my_check(message1):
      return message1.content.startswith(',')==False and message1.channel == message.channel and message1.author == message.author

    i = -1
    correct = False
    sizes = [0.05, 0.1, 0.2, 0.3, 0.5, 1.0]
    skip = False
    # loop for cropped images
    #print(i, correct, terminate, skip)
    while(i < 5 and not correct and not terminate and not skip):
      i += 1
      # get filepath for a cropped image
      new_filepath = cropper(filepath, sizes[i])
      try:
        await message.channel.send(file=discord.File(new_filepath))
      except:
        await message.channel.send("Something went wrong :(")
        terminate = True
      going = False
      skip = False
      while(not going):
        try:
          msg = await client.wait_for('message', check=my_check, timeout = 600)
          if(msg.content.startswith('.end')):
            await message.channel.send(file=discord.File(filepath))
            answer_embed = discord.Embed(title="")
            answer_embed.add_field(name="Artist", value=artist, inline=True)
            answer_embed.add_field(name = "Title", value=title, inline=True)
            answer_embed.add_field(name = "Date", value=date, inline=True)
            await message.channel.send(embed=answer_embed)
            game_over_embed = discord.Embed(title="Game Over!")
            game_over_embed.add_field(name="1st clue:", value=user_scores[0])
            game_over_embed.add_field(name="2nd clue:", value=user_scores[1])
            game_over_embed.add_field(name="3rd clue:", value=user_scores[2])
            game_over_embed.add_field(name="4th clue:", value=user_scores[3])
            game_over_embed.add_field(name="5th clue:", value=user_scores[4])
            game_over_embed.add_field(name="6th clue:", value=user_scores[5])
            game_over_embed.add_field(name="Total questions played:", value=max_score)
            await message.channel.send(embed=game_over_embed)
            terminate = True
            going = True
            shutil.rmtree('./images/{}'.format(message.channel.id))
            active_channels.remove(message.channel.id)
          elif(msg.content.startswith('.score')):
            game_over_embed = discord.Embed(title="Score")
            game_over_embed.add_field(name="1st clue:", value=user_scores[0])
            game_over_embed.add_field(name="2nd clue:", value=user_scores[1])
            game_over_embed.add_field(name="3rd clue:", value=user_scores[2])
            game_over_embed.add_field(name="4th clue:", value=user_scores[3])
            game_over_embed.add_field(name="5th clue:", value=user_scores[4])
            game_over_embed.add_field(name="6th clue:", value=user_scores[5])
            game_over_embed.add_field(name="Total questions played:", value=max_score)
            await message.channel.send(embed=game_over_embed)
          elif(msg.content.startswith('.skip')):
            await message.channel.send(file=discord.File(filepath))
            answer_embed = discord.Embed(title="")
            answer_embed.add_field(name="Artist", value=artist, inline=True)
            answer_embed.add_field(name = "Title", value=title, inline=True)
            answer_embed.add_field(name = "Date", value=date, inline=True)
            await message.channel.send(embed=answer_embed)
            await msg.channel.send("Skipping current question...")
            going = True
            skip = True
            shutil.rmtree('./images/{}'.format(message.channel.id))
          elif(msg.content.startswith('.')):
            print("")
          else:
            print("{} guessed: {}".format(msg.author.name, msg.content))
            going = True
        except asyncio.TimeoutError:
          await message.channel.send("Your game has timed out")
          await message.channel.send(file=discord.File(filepath))
          answer_embed = discord.Embed(title="")
          answer_embed.add_field(name="Artist", value=artist, inline=True)
          answer_embed.add_field(name = "Title", value=title, inline=True)
          answer_embed.add_field(name = "Date", value=date, inline=True)
          await message.channel.send(embed=answer_embed)
          
          game_over_embed = discord.Embed(title="Game Over!")
          game_over_embed.add_field(name="1st clue:", value=user_scores[0])
          game_over_embed.add_field(name="2nd clue:", value=user_scores[1])
          game_over_embed.add_field(name="3rd clue:", value=user_scores[2])
          game_over_embed.add_field(name="4th clue:", value=user_scores[3])
          game_over_embed.add_field(name="5th clue:", value=user_scores[4])
          game_over_embed.add_field(name="6th clue:", value=user_scores[5])
          game_over_embed.add_field(name="Total questions played:", value=max_score)
          await message.channel.send(embed=game_over_embed)
          
          terminate = True
          going = True
          shutil.rmtree('./images/{}'.format(message.channel.id))
          active_channels.remove(message.channel.id)
          
      if(not terminate and not skip):
        if(use_artist):
          answers = artist
          re.sub("[\(\[].*?[\)\]]", "", answers)
          answers = answers.lower().strip(" ").split(" ")
          user_answers = msg.content.lower().strip(" ").split(" ")
        else:
          answers = [x.strip(" ") for x in title.lower().split("/")]
          user_answers = [msg.content.lower().strip(" ")]
        found = False
        for answer in answers:
          for user_answer in user_answers:
            if(fuzz.ratio(user_answer, answer) >= 65):
              found = True
        if(found):
          await msg.channel.send("**Correct!**")
          await message.channel.send(file=discord.File(filepath))
          answer_embed = discord.Embed(title="")
          answer_embed.add_field(name="Artist", value=artist, inline=True)
          answer_embed.add_field(name = "Title", value=title, inline=True)
          answer_embed.add_field(name = "Date", value=date, inline=True)
          await message.channel.send(embed=answer_embed)
          await msg.channel.send("Loading next artwork, commands not accepted during this time...")
          shutil.rmtree('./images/{}'.format(message.channel.id))
          user_score += 1
          user_scores[i] += 1
          max_score += 1
          correct = True
        else:
          await msg.channel.send("**Incorrect!**")
    if(not correct and not skip and not terminate):
      await msg.channel.send("Out of guesses!")
      max_score += 1
      answer_embed = discord.Embed(title="")
      answer_embed.add_field(name="Artist", value=artist, inline=True)
      answer_embed.add_field(name = "Title", value=title, inline=True)
      answer_embed.add_field(name = "Date", value=date, inline=True)
      await message.channel.send(embed=answer_embed)
      await msg.channel.send("Loading next artwork, commands not accepted during this time...")
      shutil.rmtree('./images/{}'.format(message.channel.id))

async def multiplayer_game(message, use_artist, easy, num_questions):
  active_channels.append(message.channel.id)
  await message.channel.send('Starting your game...')
  user_scores = {}
  user_scores[message.author.name] = [0,0,0,0]
  await message.channel.send("Each clue is shown for 5 seconds, send 'buzz' to buzz on a question, after which you will have 10 seconds to answer. +15 in the first two clues, +10 if correct, -5 if wrong before the last clue, can only buzz once per question")

  # loop for the number of questions to be played
  j = 0
  while(j < num_questions):
    j += 1
    worked = False
    if(j > 1):
      scores_embed = discord.Embed(title="Scores")
      for p in sorted(user_scores.items(), key=lambda item: item[1][0], reverse=True):
        scores_embed.add_field(name = p[0], value="**" + str(p[1][0]) + "**" + " ({}/{}/{})".format(p[1][1], p[1][2], p[1][3]), inline=False)
      await message.channel.send(embed=scores_embed)
    await message.channel.send("Loading next artwork, commands not accepted during this time...")
    artist, title, date, link, filepath = choose_painting(message, easy, "")
    if(use_artist):
      print("{}: {}".format(message.author.name, artist))
    else:
      print("{}: {}".format(message.author.name, title))
    await message.channel.send("**Question {} of {}**".format(j, num_questions))
    if(use_artist):
      await message.channel.send("Name the artist of the following artwork:")
    else:
      await message.channel.send("Give the title of the following artwork:")

    def buzz_check(message1):
      return message1.content.startswith(',')==False and message1.channel == message.channel
    def answer_check(msg2):
      return buzz.channel == msg2.channel and buzz.author == msg2.author and msg2.content.startswith(',')==False
    def unpause_check(msg3):
      return msg3.channel == buzz.channel and msg3.content.lower().startswith(".unpause")

    i = -1
    sizes = [0.05, 0.1, 0.2, 0.3, 0.5, 1.0]
    correct = False
    buzzes = []
    change = True
    buzz_time = time.time()
    remaining_time = 5
    while(not change or (i < 5 and not correct)):
      # if we require the next clue, show it
      if(change):
        await message.channel.send("Loading next clue...")
        i += 1
        new_filepath = cropper(filepath, sizes[i])
        if(i == 5):
          await message.channel.send("Final clue:")
        try:
          await message.channel.send(file=discord.File(new_filepath))
        except:
          await message.channel.send("Something went wrong :(")
      else:
        change = True

      buzzed = False
      try:
        # check if user input is a command, a buzz, or neither
        # remaining_time decreases so messages don't stall it forever
        buzz_time = time.time()
        buzz = await client.wait_for('message', check=buzz_check, timeout = max(0, remaining_time))
        if(buzz.content.lower().startswith(".pause")):
          await buzz.channel.send("Game paused, type '.unpause' to resume the game")
          unpause_msg = await client.wait_for('message', check=unpause_check)
          await buzz.channel.send("Unpausing game...")
        elif(buzz.content.lower().startswith(".skip")):
          await buzz.channel.send("Skipping question...")
          j -= 1
          break
        elif(buzz.content.lower().startswith(".end") and buzz.author == message.author):
          await buzz.channel.send("Ending game...")
          j = num_questions
          break
        elif("buzz" in buzz.content.lower() and buzz.author not in buzzes):
          buzzed = True
          remaining_time -= time.time() - buzz_time
          print("{} buzzed".format(buzz.author.name))
          buzzes.append(buzz.author)
          if(buzz.author.name not in user_scores.keys()):
            user_scores[buzz.author.name] = [0,0,0,0]
        else:
          change = False
          remaining_time -= time.time() - buzz_time
          #print(remaining_time)
      except:
        correct = False
        change = True
        remaining_time = 5

      # if a user did buzz, wait for their answer
      if(buzzed):
        buzzed = False
        await buzz.channel.send(buzz.author.mention)
        try:
          msg = await client.wait_for('message', check=answer_check, timeout = 10)
          print("{} guessed: {}".format(msg.author.name, msg.content))
          # compare user answer to correct answer
          if(use_artist):
            answers = artist
            re.sub("[\(\[].*?[\)\]]", "", answers)
            answers = answers.lower().strip(" ").split(" ")
            user_answers = msg.content.lower().strip(" ").split(" ")
          else:
            answers = [x.strip(" ") for x in title.lower().split("/")]
            user_answers = [msg.content.lower().strip(" ")]
          correct = False
          for answer in answers:
            for user_answer in user_answers:
              if(fuzz.ratio(user_answer, answer) >= 65):
                correct = True
          if(correct):
            if(i < 2):
              await msg.channel.send("**Correct!** +15")
              user_scores[msg.author.name][1] += 1
              user_scores[msg.author.name][0] += 15
            else:
              await msg.channel.send("**Correct!** +10")
              user_scores[msg.author.name][2] += 1
              user_scores[msg.author.name][0] += 10
            await message.channel.send(file=discord.File(filepath))
            answer_embed = discord.Embed(title="Answer:")
            answer_embed.add_field(name="Artist", value=artist, inline=True)
            answer_embed.add_field(name = "Title", value=title, inline=True)
            answer_embed.add_field(name = "Date", value=date, inline=True)
            await message.channel.send(embed=answer_embed)
            # if(j < num_questions):
            #   scores_embed = discord.Embed(title="Scores")
            #   for p in sorted(user_scores.items(), key=lambda item: item[1][0], reverse=True):
            #     scores_embed.add_field(name = p[0], value="**" + str(p[1][0]) + "**" + " ({}/{}/{})".format(p[1][1], p[1][2], p[1][3]), inline=False)
            #   await message.channel.send(embed=scores_embed)
            shutil.rmtree('./images/{}'.format(message.channel.id))
            buzzes = []
          else:
            change = False
            if(i != 5):
              await msg.channel.send("**Incorrect!** -5")
              user_scores[msg.author.name][3] += 1
              user_scores[msg.author.name][0] -= 5
            else:
              await msg.channel.send("**Incorrect!** No penalty")
        except:
          if(i != 5):
            await buzz.channel.send("**Out of time!** -5")
            user_scores[msg.author.name][3] += 1
            user_scores[msg.author.name][0] -= 5
          else:
            await buzz.channel.send("**Out of time!** No penalty")
          change = False

    if(not correct and (change or remaining_time <= 0)):
      await message.channel.send(file=discord.File(filepath))
      answer_embed = discord.Embed(title="Answer:")
      answer_embed.add_field(name="Artist", value=artist, inline=True)
      answer_embed.add_field(name = "Title", value=title, inline=True)
      answer_embed.add_field(name = "Date", value=date, inline=True)
      await message.channel.send(embed=answer_embed)
      shutil.rmtree('./images/{}'.format(message.channel.id))
      buzzes = []

  scores_embed = discord.Embed(title="Game Over!")
  for p in sorted(user_scores.items(), key=lambda item: item[1][0], reverse=True):
    scores_embed.add_field(name = p[0], value="**" + str(p[1][0]) + "**" + " ({}/{}/{})".format(p[1][1], p[1][2], p[1][3]), inline=False)
  await message.channel.send(embed=scores_embed)
  active_channels.remove(message.channel.id)
  

client = discord.Client()

@client.event
async def on_ready():
  print("Logged in as {0.user}".format(client))
  # clear active channels
  active_channels = []
  # clear all image subfolders
  if(os.path.isdir('./images/')):
    shutil.rmtree('./images/')
  os.makedirs('./images/')
  await client.change_presence(activity=discord.Game(name=".help for info!"))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith(".restart") and message.author.id == developer_id:
    active_channels.append(message.channel.id)
    for channel_id in active_channels:
      print(channel_id)
      channel = client.get_channel(channel_id)
      await channel.send("The bot is being restarted for development purposes, sorry for any inconvenience")
    active_channels.remove(message.channel.id)

  if(message.content.startswith('.test')):
    print("test")

  # help menu
  if(message.content.startswith('.help')):
    embed=discord.Embed(title="Help Menu")
    embed.add_field(name=".start [artist/title] [optional crop] [optional hard/extreme] [optional startyear-endyear]", value="Examples: .start title crop 1800-1900, .start artist extreme\n.end to end your game\n.skip to skip questions (in cropped)", inline=False)
    
    embed.add_field(name=".multiplayer [artist/title] [optional hard/extreme] [optional num-questions]", value="Examples: .multiplayer artist hard, .multiplayer title 20\nIf not specified, num-questions is 10 by default\n .pause to pause the game\n .skip to skip a question\n .end to end the game (can only be done by the player who started it)", inline=False)
    
    embed.add_field(name="Settings:", value="artist/title: guess the artist or title of each artwork\n default/crop: see the entire artwork at once, or see progressively larger fragments\n default/hard/extreme: default dataset has been manually curated, hard dataset has ~28000 artworks by ~250 artists, extreme dataset has ~86000 artworks by ~3400 artists\n startyear-endyear: only shows you artworks created within the specified date range", inline=False)
    await message.channel.send(embed=embed)

  

  
  if message.content.startswith('.start') and message.channel.id not in active_channels:
    print(message.author.name)
    msg = message.content[len(".start"):]
    msg = msg.replace(" ", "")
    crop = False
    use_artist = False
    valid = True
    easy = 0
  
    if(msg.startswith("artist")):
      use_artist = True
      msg = msg[len("artist"):]
    elif(msg.startswith("title")):
      use_artist = False
      msg = msg[len("title"):]
    else:
      await message.channel.send("Invalid command, please see .help for formatting")
      valid = False
      
    if(msg.startswith("crop")):
      crop = True
      msg = msg[len("crop"):]
    else:
      crop = False
      
    if(msg.startswith("hard")):
      easy = 1
      msg = msg[len("hard"):]
    elif(msg.startswith("extreme")):
      easy = 2
      msg = msg[len("extreme"):]
    else:
      easy = 0

    if(valid):
      query = msg
      #print(message, use_artist, easy, query)
      if(crop):
        print("{} is starting cropped, Difficulty={}".format(message.author.name, str(easy)))
        await cropped_game(message, use_artist, easy, query)
        print("{} is ending cropped, Difficulty={}".format(message.author.name, str(easy)))
      else:
        print("{} is starting uncropped, Difficulty={}".format(message.author.name, str(easy)))
        await uncropped_game(message, use_artist, easy, query)
        print("{} is ending uncropped, Difficulty={}".format(message.author.name, str(easy)))
        

  # .multiplayer [artist/title] [optional hard] [optional num_questions]
  if message.content.startswith('.multiplayer') and message.channel.id not in active_channels:
    msg = message.content[len(".multiplayer"):]
    msg = msg.replace(" ", "")
    use_artist = False
    valid = True
    easy = 0
    num_questions = 10
  
    if(msg.startswith("artist")):
      use_artist = True
      msg = msg[len("artist"):]
    elif(msg.startswith("title")):
      use_artist = False
      msg = msg[len("title"):]
    else:
      await message.channel.send("Invalid command, please see .help for formatting")
      valid = False
      
    if(msg.startswith("hard")):
      easy = 1
      msg = msg[len("hard"):]
    elif(msg.startswith("extreme")):
      easy = 2
      msg = msg[len("extreme"):]
    else:
      easy = 0

    if(len(msg) > 0 and msg.isdigit()):
      num_questions = int(msg)
    else:
      num_questions = 10

    if(valid):
      print("{} is starting multiplayer, Difficulty={}".format(message.author.name, str(easy)))
      await multiplayer_game(message, use_artist, easy, num_questions)
      print("{} is ending multiplayer, Difficulty={}".format(message.author.name, str(easy)))
        

# try:
#   client.run(TOKEN)
#   print("Bot running")
# except:
#   print("Attempting to restart...")
#   #time.sleep(5)
#   os.system("kill 1")

client.run(TOKEN)