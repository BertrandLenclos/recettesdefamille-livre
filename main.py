from exportMediaWiki2Html import request_pages
from bs4 import BeautifulSoup

def main():
    with open('template.html') as template:
        content = template.read()
        soup = BeautifulSoup(content, 'html.parser')
        for page in request_pages():
            soup.body.append(page)
        f = open("index.html", "wb")
        f.write(soup.prettify().encode('utf-8'))
        f.close()

if __name__ == '__main__':
    main()
