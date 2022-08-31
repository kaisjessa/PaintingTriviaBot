import urllib.request
import json
import random
import pandas as pd
import PIL
from PIL import Image
import random
import math

  
# https://collectionapi.metmuseum.org/public/collection/v1/search?isHighlight=true&q=sunflowers
# https://collectionapi.metmuseum.org/public/collection/v1/objects/[objectID]

# chooses random painting id searched with args
# saves painting image to folder

'''
def choose_painting(args="the"):
  if(len(args)==0):
    args = "the"
  print("ARGS:", args)
  with urllib.request.urlopen("https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&departmentId=11&isHighlight=true&q={}".format(args)) as url:
    data = json.loads(url.read().decode())
    if(data['objectIDs'] is None):
      print("No paintings with query found")
      return choose_painting("the")
    max_index = len(data['objectIDs'])
    print(max_index)
    painting_id = data['objectIDs'][random.randint(0, max_index)-1]
    
  print(painting_id)
  with urllib.request.urlopen("https://collectionapi.metmuseum.org/public/collection/v1/objects/{}".format(painting_id)) as url:
    data = json.loads(url.read().decode())
    print(data["primaryImage"])
    print(data["title"])
    print(data["artistDisplayName"])
    link = data["primaryImage"]
    painter = data["artistDisplayName"]
    title = data["title"]
    date = data["objectDate"]
    if(data["primaryImage"] == "" or data["title"] == "" or data["artistDisplayName"]==""):
      return choose_painting(args)

  return painter, title, date, link



def choose_painting2(args=""):
  args = args.split("-")
  if(len(args) != 2 or not args[0].isdigit() or not args[1].isdigit()):
    args = ""
  df=pd.read_csv("databases/catalog.csv")
  df = df[df.FORM == "painting"]
  if(args != ""):
    print(args[0], args[1])
    df2 = df.copy()
    df2 = df2[df2['DATE'].apply(lambda x: str(x).isdigit())]
    df2["DATE"] = pd.to_numeric(df2["DATE"])
    df2 = df2[df2['DATE'].between(int(args[0]), int(args[1]), 'both')]
    if(len(df2.index) == 0):
      print("Nothing in the range {} to {}".format(args[0], args[1]))
      df2 = df
    else:
      df = df2
  row = df.sample().iloc[0]
  print(row)
  link = row["URL"].replace("/html/", "/art/").replace(".html", ".jpg")
  painter = row["AUTHOR"]
  title = row["TITLE"]
  date = row["DATE"]
  print(painter, title, date, link)
  return painter, title, date, link

'''

def choose_painting3(easy = False, args=""):
  #print("here")
  args = args.split("-")
  if(len(args) != 2 or not args[0].isdigit() or not args[1].isdigit()):
    args = ""
  if(easy == 0):
    file = "databases/easy.csv"
  elif(easy == 1):
    file = "databases/harder_shuffled.csv"
  else:
    file = "databases/extreme.csv"
  df=pd.read_csv(file)
  df2 = df.copy()
  if(args != ""):
    #print(args[0], args[1])
    df2 = df2[df2['YEAR'].apply(lambda x: str(x).isdigit())]
    df2["YEAR"] = pd.to_numeric(df2["YEAR"])
    df2 = df2[df2['YEAR'].between(int(args[0]), int(args[1]), 'both')]
    if(len(df2.index) == 0):
      #print("Nothing in the range {} to {}".format(args[0], args[1]))
      df2 = df.copy()
  row = df2.sample().iloc[0]
  #print(row)
  link = row["LINK"]
  painter = row["ARTIST"]
  title = row["TITLE"]
  date = row["YEAR"]
  #print(painter, title, date, link)
  return painter, title, date, link

'''
def filter_file(filepath):
  db = pd.read_csv(filepath)
  df2 = db.copy()
  print(df2.columns)
  df2 = df2[df2['YEAR'].apply(lambda x: str(x).isdigit())]
  df2["YEAR"] = pd.to_numeric(df2["YEAR"])
  df2 = df2[df2['YEAR'].between(0, 2022, 'both')]
  df2.to_csv('databases/artists_filtered.csv', sep=',', encoding='utf-8')
'''
#filter_file("databases/artists.csv")

def cropper(filepath, size):
  if(size == 1.0):
    return filepath
  image = Image.open(filepath)
  width, height = image.size

  new_height = int(height * size)
  new_width = int(width * size)

  y = random.randint(0, height - new_height)
  x = random.randint(0, width - new_width)

  area = (x, y, x + new_width, y + new_height)
  new_image = image.crop(area)
  new_image = new_image.convert('RGB')

  new_filepath = filepath[:-5] + "_" + str(size) + ".jpeg"
  new_image.save(new_filepath)
  return new_filepath