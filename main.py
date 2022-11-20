from exportMediaWiki2Html import request_pages, request_familles_de_recettes
from bs4 import BeautifulSoup
import recettes_maker
import json
import unicodedata

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

def get_data():
    print('\nRÉCUPÉRATION DES DONNÉES SUR LE NET\n')
    print('Récupération de l\'index du livre...')
    index = get_index()
    categories_index = get_index_categories()

    print('Récupération des recettes...')
    recettes = sorted(request_pages(category=18), key=lambda r: strip_accents(r['title']))
    
    print('Récupération des pages spéciales...')
    special_pages = {id:request_pages(page=int(id))[0] for id in filter(lambda s: s.isdigit(), index)}

    print('Récupération des catégories...')
    for page in recettes:
        page['categories'] = request_familles_de_recettes(page['title'])

    print('Création du sommaire...')
    sommaire = []
    for item in index:
        print('-> Ajout dans le sommaire de ' + item)
        if item == 'recettes':
            recettes_sommaire = []
            print(f'-> Ajout dans le sommaire des {len(recettes)} recettes')
            for page in recettes:
                recettes_sommaire.append({'title':page['title'], 'pageid':page['title']})
            sommaire.append({'title':"Recettes", 'content':recettes_sommaire})
        elif item == 'sommaire':
            sommaire.append({'title':"Sommaire", 'pageid':"Sommaire"})
        elif item == 'index':
            sommaire.append({'title':"Index", 'pageid':"Index"})
        else:
            page = special_pages[item]
            sommaire.append({'title':page['title'], 'pageid':page['title']})

    print('Création de l\'index par catégories...')
    for page in recettes:
        for category in page['categories']:
            for cat in categories_index:
                if cat['name'] == category:
                    cat['recettes'].append(page['title'])

    data = {
        'index':index,
        'recettes':recettes,
        'special_pages':special_pages,
        'sommaire':sommaire,
        'categories_index':categories_index,
    }

    return data

def store_data_json(data):
    print('\nMISES EN CACHE DES DONNÉES\n')
    print('-> Écriture recettes.json...')
    with open('recettes.json', 'w') as fi:
        json.dump(data, fi)

def get_data_json():
    print('\nLECTURE DES DONNÉES MISES EN CACHE\n')
    print('-> Lecture de recettes.json...')
    with open('recettes.json', 'r') as fi:
        return json.load(fi)

def create_book(data):
    print('\nCRÉATION DU LIVRE\n')
    with open('template.html') as template:
        content = template.read()
        soup = BeautifulSoup(content, 'html.parser')
        for item in data['index']:
            print('-> Creation de ' + item)
            if item == 'recettes':
                for page in data['recettes']:
                    print('-> Creation de', page['title'])
                    recette = recettes_maker.parse_recette(page['title'], page['content'], page['categories'])
                    soup.body.append(recette)
            elif item == 'sommaire':
                soup.body.append(recettes_maker.parse_sommaire(data['sommaire']))
            elif item == 'index':
                soup.body.append(recettes_maker.parse_index(data['categories_index']))
                # soup.body.append(placeholder('ici il y aura l\'index par categories'))
            else:
                page = data['special_pages'][item]
                soup.body.append(recettes_maker.parse_page(page['title'], page['content']))

        f = open("index.html", "wb")
        f.write(soup.encode('utf-8'))
        f.close()


def main(cache=False):
    data = {}
    if cache:
        data = get_data_json()
    else:
        data = get_data()
        store_data_json(data)
    create_book(data)


def placeholder(content):
    soup = BeautifulSoup()
    article = soup.new_tag('article')
    article.append(content)
    return article


def get_index():
    index_page = request_pages(page=901)[0]['content']
    soup = BeautifulSoup(index_page, 'html.parser')
    items = soup.find_all('li')
    def clean_item(item) : return item.get_text().split('#')[0].strip()
    return list(map(clean_item, items))

def get_index_categories():
    index_page = request_pages(page=1166)[0]['content']
    soup = BeautifulSoup(index_page, 'html.parser')
    items = soup.find_all('li')
    def clean_item(item) : return {'name':item.get_text().strip(), 'recettes':[]}
    return list(map(clean_item, items))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Création du livre recettes de famille.')
    parser.add_argument('--cache', action='store_true', help='Get data from cache')
    args = parser.parse_args()
    main(cache=args.cache)
