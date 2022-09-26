from bs4 import BeautifulSoup, Comment
import copy

def parse_recette(title, content):
    soup_in = BeautifulSoup(content, 'html.parser')
    remove_divs(soup_in)
    remove_sups(soup_in)
    remove_tables(soup_in)


    soup_out = BeautifulSoup()

    article = soup_out.new_tag('article')
    main = soup_out.new_tag('main')
    aside = soup_out.new_tag('aside')

    soup_out.append(article)
    article.append(aside)
    article.append(main)


    # - INFOS = pour n personnes + temps…
    # - INGRÉDIENTS

    aside.append(get_infos(soup_in))
    aside.append(get_ingredients(soup_in))

    main.append(get_title(soup_in, title))
    main.append(get_description(soup_in))
    main.append(get_auteurs(soup_in))
    main.append(get_contexte(soup_in))
    main.append(get_recette(soup_in))
    main.append(get_astuces(soup_in))
    main.append(get_tags(soup_in))

    add_top_comment(soup_out, title)
    return soup_out
    pass


def get_infos(soup):
    return new_section(soup, 'Temps_de_préparation', 'infos')

def get_ingredients(soup):
    return new_section(soup, 'Ingrédients', 'ingredients')

def new_section(soup, heading_id, cls):
    section = soup.new_tag('section', attrs={"class":cls})

    try:
        heading = soup.find(id=heading_id).parent
    except AttributeError:
        print('                   OUPS pas de ' + heading_id)
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

def get_auteurs(soup):
    return new_section(soup, 'Auteurs', 'auteurs')

def get_contexte(soup):
    return new_section(soup, 'Contexte', 'contexte')

def get_recette(soup):
    return new_section(soup, 'Préparation', 'recette')

def get_astuces(soup):
    return new_section(soup, 'Astuces', 'astuces')

def get_tags(soup):
    section = soup.new_tag('section', attrs={"class":'tags'})
    ul = soup.new_tag('ul')
    section.append(ul)
    for content in ['Tags', 'autre tag', 'coucou']:
        tag = soup.new_tag('li', attrs={"class":'tag'})
        tag.append(content)
        ul.append(tag)
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
