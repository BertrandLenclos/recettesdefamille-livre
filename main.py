from exportMediaWiki2Html import request_pages, request_familles_de_recettes
from bs4 import BeautifulSoup
import recettes_maker

def main():
    print('creation du livre...')
    with open('template.html') as template:
        content = template.read()
        soup = BeautifulSoup(content, 'html.parser')

        index = get_index()
        recettes = request_pages(category=18)

        # creation sommaire et index
        categories_index = {}
        sommaire = []
        for item in index:
            print('integration dans le sommaire de la partie ' + item)
            if item == 'recettes':
                recettes_sommaire = []
                for page in recettes:
                    recettes_sommaire.append({'title':page['title'], 'pageid':page['title']})
                    print('integration des recettes dans l\'index')
                    page['categories'] = request_familles_de_recettes(page['title'])
                    for category in page['categories']:
                        if not category in categories_index :
                            categories_index[category] = []
                        categories_index[category].append(page['title'])
                sommaire.append({'title':"Les recettes", 'content':recettes_sommaire})
            elif item == 'sommaire':
                sommaire.append({'title':"Sommaire", 'pageid':"Sommaire"})
            elif item == 'index':
                sommaire.append({'title':"Index", 'pageid':"Index"})
            else:
                page = request_pages(page=int(item))[0]
                sommaire.append({'title':page['title'], 'pageid':page['title']})

        print(sommaire)
        print(categories_index)

        # creation pages 
        for item in index:
            print('creation de la partie ' + item)
            if item == 'recettes':
                for page in request_pages(category=18):
                    recette = recettes_maker.parse_recette(page['title'], page['content'], page['categories'])
                    soup.body.append(recette)
            elif item == 'sommaire':
                soup.body.append(placeholder('ici il y aura le sommaire'))
            elif item == 'index':
                soup.body.append(placeholder('ici il y aura l\'index par categories'))
            else:
                page = request_pages(page=int(item))[0]
                soup.body.append(recettes_maker.parse_page(page['title'], page['content']))


        f = open("index.html", "wb")
        f.write(soup.encode('utf-8'))
        f.close()

def placeholder(content):
    soup = BeautifulSoup()
    article = soup.new_tag('article')
    article.append(content)
    return article

    return article


def get_index():
    index_page = request_pages(page=901)[0]['content']
    soup = BeautifulSoup(index_page, 'html.parser')
    items = soup.find_all('li')
    def clean_item(item) : return item.get_text().split('#')[0].strip()
    return map(clean_item, items)


if __name__ == '__main__':
    main()
