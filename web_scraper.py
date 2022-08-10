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

artists = scrape_artists()

def is_valid(url):
  try:
    res = requests.get(url)
    return res.ok
  except:
    return False

def make_file():
  with open('databases/artists.csv', 'w') as f:
    f.write("ARTIST,TITLE,YEAR,LINK")
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

make_file()