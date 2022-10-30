from bs4 import BeautifulSoup, Comment
import copy

def new_article(title):
    soup = BeautifulSoup()
    article = soup.new_tag('article')
    article['id'] = title.replace(' ', '_')
    return article

def parse_page(title, content):
    soup_in = BeautifulSoup(content, 'html.parser')
    remove_divs(soup_in)
    remove_sups(soup_in)
    remove_tables(soup_in)
    h1 = soup_in.new_tag('h1')
    h1.append(title)


    article = new_article(title)
    article.append(h1)
    article.append(soup_in.div)

    return article


def new_page_link(title):
    soup = BeautifulSoup()
    a = soup.new_tag('a')
    a['href'] = '#' + title.replace(' ', '_')
    a['class'] = 'pagelink'
    a.append(title)
    return a


def parse_index(index):
    title='Index'
    soup = BeautifulSoup()
    article = new_article(title)

    h1 = soup.new_tag('h1')
    ul = soup.new_tag('ul')
    article.append(h1)
    article.append(ul)
    h1.append(title)
    for category, recettes in index.items():
        li = soup.new_tag('li')
        h2 = soup.new_tag('h2')
        h2.append(category)
        ul2 = soup.new_tag('ul')
        for title in recettes:
            li2 = soup.new_tag('li')
            li2.append(new_page_link(title))
            ul2.append(li2)
        li.append(h2)
        li.append(ul2)
        ul.append(li)
    return article


def parse_sommaire(sommaire):
    title = 'Sommaire'
    soup = BeautifulSoup()
    article = new_article(title)

    h1 = soup.new_tag('h1')
    ul = soup.new_tag('ul')
    article.append(h1)
    article.append(ul)
    h1.append(title)
    for item in sommaire:
        li = soup.new_tag('li')
        h2 = soup.new_tag('h2')

        h2_content = item['title'] if 'content' in item else new_page_link(item['title'])
        h2.append(h2_content)
        li.append(h2)
        if 'content' in item:
            ul2 = soup.new_tag('ul')
            for recette in item['content']:
                li2 = soup.new_tag('li')
                li2.append(new_page_link(recette['title']))
                ul2.append(li2)
            li.append(ul2)
        ul.append(li)
    return article


def parse_recette(title, content, categories):
    soup_in = BeautifulSoup(content, 'html.parser')

    images = get_images(soup_in)

    remove_divs(soup_in)
    remove_sups(soup_in)
    remove_tables(soup_in)


    soup_out = BeautifulSoup()


    article = new_article(title)
    article['class']='recette'
    main = soup_out.new_tag('main')
    aside = soup_out.new_tag('aside')


    # - INFOS = pour n personnes + temps…
    # - INGRÉDIENTS

    aside.append(get_infos(soup_in))
    aside.append(get_ingredients(soup_in))

    main.append(get_tags(soup_in, categories))
    main.append(get_title(soup_in, title))
    main.append(get_description(soup_in))
    main.append(soup_out.new_tag('hr'))

    main.append(get_auteurs(soup_in))
    main.append(get_contexte(soup_in))
    main.append(soup_out.new_tag('hr'))
    main.append(get_recette(soup_in))

    astuces = get_astuces(soup_in)
    section_accompagnement = get_accompagnement(soup_in)
    if section_accompagnement.find('p'):
        li_accompagnement = create_astuce_item_from_section(soup_in, "En accompagnement", section_accompagnement)
        if not astuces.find("ul"):
            astuces.append(soup_in.new_tag('ul'))
        astuces.find("ul").insert(0, li_accompagnement)

    section_ce_quon_boit = get_ce_quon_boit(soup_in)
    if section_ce_quon_boit.find('p'):
        li_ce_quon_boit = create_astuce_item_from_section(soup_in, "Ce qu'on boit avec ça", section_ce_quon_boit)
        if not astuces.find("ul"):
            astuces.append(soup_in.new_tag('ul'))
        astuces.find("ul").append(li_ce_quon_boit)

    if astuces.find("ul"):
        main.append(soup_out.new_tag('hr'))
        main.append(astuces)


    add_top_comment(soup_out, title)
    article.append(aside)
    article.append(main)


    for image in images:
        if image and image.attrs['data-position'] == 'avant':
            soup_out.append(create_images(soup_in, image))

    soup_out.append(article)


    for image in images:
        if image and image.attrs['data-position'] == 'dans':
            article.append(create_images(soup_in, image))

        elif image and image.attrs['data-position'] == 'petit':
            main.append(create_images(soup_in, image))

        elif image and image.attrs['data-position'] == 'apres':
            soup_out.append(create_images(soup_in, image))
            



    return soup_out
    
def create_images(soup, images):
    position = images.attrs['data-position']
    div = soup.new_tag('div', attrs={"class":'images '+position})
    image1 = images.attrs['data-image1']
    image2 = images.attrs['data-image2']
    if image1 : div.append(soup.new_tag('img', attrs={'src':image1}))
    if image2 : div.append(soup.new_tag('img', attrs={'src':image2}))
    return div


def create_astuce_item_from_section(soup, name, section):
    content = section.find('p').get_text()
    content = content[0].lower() + content[1:]
    li = soup.new_tag('li')
    em = soup.new_tag('em')
    em.append(name)
    li.append(em)
    li.append(' : ')
    li.append(content)
    return li

def get_infos(soup):
    return new_section(soup, 'Temps_de_préparation', 'infos')

def get_ingredients(soup):
    return new_section(soup, 'Ingrédients', 'ingredients')

def get_images (soup):
    return soup.find_all(attrs={'class':'imagedulivre'})

def new_section(soup, heading_id, cls):
    section = soup.new_tag('section', attrs={"class":cls})

    try:
        heading = soup.find(id=heading_id).parent
    except AttributeError:
        # print('---> pas de ' + heading_id)
        return section

    for sibling in heading.next_siblings:
        if sibling.name == 'h2' or sibling.name == 'h3' or sibling.name == 'h4':
            break
        section.append(copy.copy(sibling))
    return section

def get_description(soup):
    section = soup.new_tag('section', attrs={"class":'description'})
    section.append(copy.copy(soup.p))
    return section

def get_ce_quon_boit(soup):
    return new_section(soup, "Ce_qu'on_boit_avec_ça", 'cequonboit')

def get_accompagnement(soup):
    return new_section(soup, 'En_accompagnement', 'accompagnement')

def get_auteurs(soup):
    return new_section(soup, 'Auteurs', 'auteurs')

def get_contexte(soup):
    return new_section(soup, 'Contexte', 'contexte')

def get_recette(soup):
    return new_section(soup, 'Préparation', 'recette')

def get_astuces(soup):
    return new_section(soup, 'Astuces', 'astuces')

def get_tags(soup, categories):
    section = soup.new_tag('section', attrs={"class":'tags'})
    div = soup.new_tag('div')
    div.append(' – '.join(categories))
    section.append(div)
    # for content in categories:
    #     tag = soup.new_tag('li', attrs={"class":'tag'})
    #     tag.append(content)
    #     div.append(content)
    return section

def get_title(soup, txt):
    title = soup.new_tag('h1')
    title.append(txt)
    return title

def add_top_comment(soup, txt):
    comment = Comment(txt.center(70, '-'))
    soup.insert(0, comment)

def remove_divs(soup):
    div = soup.div.div
    while(div):
        div.extract()
        div = soup.div.div

def remove_sups(soup):
    for sup in soup.find_all('sup') :
        sup.extract()

def remove_tables(soup):
    table = soup.div.table
    while(table):
        table.extract()
        table = soup.div.table


def has_class_but_no_id(tag):
    return tag.has_attr('class') and not tag.has_attr('id')
