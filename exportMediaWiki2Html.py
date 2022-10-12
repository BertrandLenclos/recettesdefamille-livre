#!/usr/bin/python3

# Author: Timotheus Pokorra <timotheus.pokorra@solidcharity.com>
# source hosted at https://github.com/SolidCharity/exportMediaWiki2HTML
# licensed under the MIT license
# Copyright 2020-2021 Timotheus Pokorra

from urllib import parse
import requests
import json
import re
from pathlib import Path
import argparse

downloadedimages = []


def request_categories(title):
  S = requests.Session()

  URL = "http://recettesdefamille.wiki/api.php"

  PARAMS = {
      "action": "query",
      "format": "json",
      "prop": "categories",
      "titles": title
  }

  R = S.get(url=URL, params=PARAMS)
  data = R.json()
  
  pages = data['query']['pages']
  page = pages.popitem()[1]
  if not 'categories' in page: return []

  return list(map(lambda c: c['title'], page['categories']))

def request_familles_de_recettes(title):
  print('-> récupération des catégories pour ' + title)

  CAT = 'Catégorie:Famille de recette'
  categories = request_categories(title)
  categories = filter(lambda c: CAT in request_categories(c), categories)
  categories = map(lambda c: c.split(':')[1], categories)
  return list(categories)

def request_pages(page=-1, category=-1):
    url = "http://recettesdefamille.wiki/"
    subpath = url[url.index("://") + 3:]
    subpath = subpath[subpath.index("/")+1:]
    numberOfPages = 'max'
    pageOnly = page
    categoryOnly = category # Recettes = 18

    S = requests.Session()

    # Retrieve login token first
    PARAMS_0 = {
      'action':"query",
      'meta':"tokens",
      'type':"login",
      'format':"json"
    }
    R = S.get(url=url + "/api.php", params=PARAMS_0)
    DATA = R.json()
    LOGIN_TOKEN = DATA['query']['tokens']['logintoken']

    # Main-account login via "action=login" is deprecated and may stop working without warning. To continue login with "action=login", see [[Special:BotPasswords]]
    PARAMS_1 = {
      'action':"login",
      'lgname':'coucou :)',
      'lgpassword':'ca va ????',
      'lgtoken':LOGIN_TOKEN,
      'format':"json"
    }

    R = S.post(url + "/api.php", data=PARAMS_1)
    DATA = R.json()
    if "error" in DATA:
        print(DATA)
        exit(-1)

    if categoryOnly != -1:
      params_all_pages = {
        'action': 'query',
        'list': 'categorymembers',
        'format': 'json',
        'cmpageid': categoryOnly,
        'cmlimit': numberOfPages
      }
    else:
      params_all_pages = {
        'action': 'query',
        'list': 'allpages',
        'format': 'json',
        'aplimit': numberOfPages
      }

    response = S.get(url + "api.php", params=params_all_pages)
    data = response.json()

    if "error" in data:
      print(data)
      if data['error']['code'] == "readapidenied":
        print()
        print("get login token here: " + url + "/api.php?action=query&meta=tokens&type=login")
        print("and then call this script with parameters: myuser topsecret mytoken")
        exit(-1)
    if categoryOnly != -1:
      pages = data['query']['categorymembers']
    else:
      pages = data['query']['allpages']

    while 'continue' in data and (numberOfPages == 'max' or len(pages) < int(numberOfPages)):
      if categoryOnly != -1:
        params_all_pages['cmcontinue'] = data['continue']['cmcontinue']
      else:
        params_all_pages['apcontinue'] = data['continue']['apcontinue']

      response = S.get(url + "api.php", params=params_all_pages)

      data = response.json()

      if "error" in data:
        print(data)
        if data['error']['code'] == "readapidenied":
          print()
          print(f'get login token here: {url}/api.php?action=query&meta=tokens&type=login')
          print("and then call this script with parameters: myuser topsecret mytoken")
          exit(-1)

      if categoryOnly != -1:
        pages.extend(data['query']['categorymembers'])
      else:
        pages.extend(data['query']['allpages'])

    ##################

    all_pages = []
    for page in pages:
        if (pageOnly > -1) and (page['pageid'] != pageOnly):
            continue

        quoted_pagename = parse.quote(page['title'].replace(' ', '_'))
        url_page = url + "index.php?title=" + quoted_pagename + "&action=render"
        print('-> récupération de ' + page['title'])
        response = S.get(url_page)

        content = response.text

        content = re.sub("(<!--).*?(-->)", '', content, flags=re.DOTALL)

        all_pages.append({
          'pageid':page['pageid'],
          'title':page['title'],
          'content':content
        })

    return all_pages
