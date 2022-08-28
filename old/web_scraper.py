# https://github.com/rkjones4/GANGogh/blob/master/misc/scrape_wiki.py

import json
import random
import pandas as pd
import urllib
import urllib.request
import requests
import string
from bs4 import BeautifulSoup


def scrape_artists():
  url = 'https://www.wikiart.org/en/popular-artists/text-list'
  html = urllib.request.urlopen(url)
  soup =  BeautifulSoup(html)
  artists = []
  for link in soup.find_all('a'):
    link = str(link.get('href'))
    if(link is not None and link.startswith('/en/') and not link.startswith('/en/artists') and not link.startswith('/en/paintings')):
      #print(link[4:])
      artists.append(link[4:])
  return artists

def featured_paintings(artist):
  try:
    url = 'https://www.wikiart.org/en/{}'.format(artist)
    res = requests.get(url)
    html = res.text
    soup = BeautifulSoup(html)
    images = []
    for link in soup.find_all('a'):
      link = str(link.get('href'))
      if(link is not None and link.startswith('/en/{}/'.format(artist)) and not link.startswith('/en/{}/all-works'.format(artist))):
        link = url.replace('/en/{}'.format(artist), link)
        #print(link)
        img_link = link.replace('www.', 'uploads0.').replace('/en/', '/images/') + '.jpg'
        #print(img_link)
        images.append(img_link)
    return list(set(images))
  except:
    print("Search did not work with", artist)

def is_valid(url):
  try:
    res = requests.get(url)
    return res.ok
  except:
    return False

def make_file():
  artists = scrape_artists()
  with open('databases/artists1.csv', 'a') as f:
    f.write("ARTIST,TITLE,YEAR,LINK")
    f.write("\n")
    for i in range(len(artists)):
      artist = artists[i]
      print(artist)
      print(i, "out of", len(artists))
      images = featured_paintings(artist)
      for image in images:
        # image link is valid and year is known
        if is_valid(image) and image[-8:][:4].isdigit():
          artist = image[image.index("/images/") + len("/images") + 1:image.rindex('/')]
          artist = artist.replace('-', ' ')
          artist = string.capwords(artist)
          
          title = image[image.rindex('/')+1:image.rindex('-')]
          title = title.replace('-', ' ')
          title = string.capwords(title)

          date = image[-8:][:4]
          entry = artist + ',' + title + ',' + date + ',' + image
          #print(entry)
          f.write(entry)
          f.write('\n')

#make_file()

def scrape_famous():
  images = []
  for j in range(1, 11):
    url = 'https://www.wikiart.org/en/popular-paintings/alltime/{}'.format(j)
    print(url)
    res = requests.get(url)
    html = res.text
    soup = BeautifulSoup(html, features="html5lib")
    for i in str(soup.findAll()).split():  
      if(i.startswith('&quot;/en/') and i.count('/') > 2):
        i = i.replace("&quot;", "").replace(",", "")
        #print(i)
        images.append('https://www.wikiart.org' + i)
  print(len(images))
  return(images)

def make_famous():
  urls = scrape_famous()
  with open('databases/famous.csv', 'a') as f:
    f.write("ARTIST,TITLE,YEAR,LINK")
    f.write("\n")
    entries = []
    for j in range(len(urls)):
      print(j, len(urls))
      url = urls[j]
      artist = ""
      title = ""
      year = ""
      link = ""
      res = requests.get(url)
      html = res.text
      soup = BeautifulSoup(html, features="html5lib")
      name = url[url.rindex('/en/')+4:]
      #print(name)
      linkFound = False
      dateFound = False
      for i in str(soup.findAll()).split():
        if(not linkFound and name in i and "uploads" in i and ".wikiart.org" in i and ".jpg" in i):
          linkFound = True
          image = i[i.index("https://uploads"):i.index(".jpg")+4]
          #print(image)
        if(not dateFound and '"dateCreated">' in i and "</span>" in i):
          dateFound = True
          year = i[i.index('"dateCreated">')+len('"dateCreated">'):i.index("</span>")]
          #print(year)
    
      if(linkFound and dateFound):
        artist = image[image.index("/images/") + len("/images") + 1:image.rindex('/')]
        artist = artist.replace('-', ' ')
        artist = string.capwords(artist)

        if image[-8:][:4].isdigit():
          title = image[image.rindex('/')+1:image.rindex('-')]
        else:
          title = image[image.rindex('/')+1:image.rindex('.jpg')]
        title = title.replace('-', ' ')
        title = string.capwords(title)

        entry = artist + ',' + title + ',' + year + ',' + image + '\n'
        print(entry)
        entries.append(entry)
    entries = list(set(entries))
    for entry in entries:
      f.write(entry)
        
def filter_file(filepath):
  db = pd.read_csv(filepath)
  df2 = db.copy()
  print(df2.columns)
  df2 = df2[df2['YEAR'].apply(lambda x: str(x).isdigit())]
  df2["YEAR"] = pd.to_numeric(df2["YEAR"])
  df2 = df2[df2['YEAR'].between(0, 2022, 'both')]
  df2.to_csv('databases/artists_filtered.csv', sep=',', encoding='utf-8')
#make_famous()
