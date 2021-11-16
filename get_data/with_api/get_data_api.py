from bs4 import BeautifulSoup
import json
import os
import tqdm
import requests
import unidecode
import urllib
from urllib.parse import urlparse
from urllib.request import urlopen
import multiprocessing
import posixpath
from goose3 import Goose
import sys
# from joblib import Parallel, delayed
from six.moves.html_parser import HTMLParser
from multiprocessing.dummy import Pool as ThreadPool
import re
from PIL import Image
import os

pattern = re.compile(r'<[^>]+>', re.S)


def resolveComponents(url):
    """
     resolveComponents('http://www.example.com/foo/bar/../../baz/bux/')
    'http://www.example.com/baz/bux/'
     resolveComponents('http://www.example.com/some/path/../file.ext')
    'http://www.example.com/some/file.ext'
    """

    parsed = urlparse(url)
    new_path = posixpath.normpath(parsed.path)
    if parsed.path.endswith('/'):
        # Compensate for issue1707768
        new_path += '/'
    cleaned = parsed._replace(path=new_path)

    return cleaned.geturl()


def get_soup(url):
    req = urllib.request.Request(url=url, headers=hdr)
    # try:
    page = urlopen(req)
    # except urllib2.HTTPError, e:
    #     print num
    #     print e.fp.read()
    soup = BeautifulSoup(page, 'html5lib')
    # [s.extract() for s in soup('script')]
    # [s.extract() for s in soup('noscript')]
    #     img = soup.find_all('img')
    figcap = soup.find_all("img")
    return soup, figcap


def retrieve_articles(m):
    articles = json.load(open("./api/nyarticles_%s_%s.json" % (year, m), 'r', encoding='utf8'))
    month_data = {}
    leftovers = {}
    len_articles = len(articles['response']['docs'])
    for num, a in enumerate(articles['response']['docs']):
        try:
            data = {}
            # using resolveComponents here, if some bad urls exist.
            url = resolveComponents(a['web_url'])
            extract = g.extract(url=url)
            # Save the data before since we might save the data inside the if
            if a['multimedia']:
                data['headline'] = a.get('headline', None)
                data['article_url'] = url
                data['article'] = unidecode.unidecode(extract.cleaned_text).replace('\n', '')
                data['abstract'] = a.get('abstract', None)
                data['article_id'] = a['_id'][14:]
                data['image'] = extract.opengraph['image']
                data['caption'] = extract.opengraph['image:alt']
                # print(url)

                img_data = requests.get(data['image'], stream=True).content
                with open(os.path.join("./images/%s.jpg" % (data['article_id'])), 'wb') as f:
                    f.write(img_data)
                with Image.open(os.path.join("./images/%s.jpg" % (data['article_id']))) as img:
                    img_size = img.size
                if img_size[0] <= 150 or img_size[0] >= 1200:  # delete head
                    os.remove(os.path.join("./images/%s.jpg" % (data['article_id'])))
                    data['caption'] = ''
                    continue
                if 'caption' in data.keys() and data['caption'] != '':
                    month_data[data['article_id']] = data
                    sys.stdout.write('\r%d/%d text documents processed...\n' % (num, len_articles))
                    sys.stdout.flush()
                else:
                    print(url)
                '''
                soup, figcap = get_soup(url)
                figcap = [c for c in figcap]
                for ix, cap in enumerate(figcap):
                    data['caption'] = pattern.sub('', cap.attrs['alt'])
                    if data['caption'] == '':
                        continue
                    img_url = resolveComponents(cap.attrs['src'])
                    img_data = requests.get(img_url, stream=True).content
                    with open(os.path.join("./images/%s.jpg" % (data['article_id'])), 'wb') as f:
                        f.write(img_data)
                    with Image.open(os.path.join("./images/%s.jpg" % (data['article_id']))) as img:
                        img_size = img.size
                    if img_size[0] <= 150 and img_size[1] <= 150: # delete head
                        os.remove(os.path.join("./images/%s.jpg" % (data['article_id'])))
                        data['caption'] = ''
                        continue
                    if 'caption' in data.keys() and data['caption'] != '':
                        month_data[data['article_id']] = data
                        sys.stdout.write('\r%d/%d text documents processed...' % (num, len_articles))
                        sys.stdout.flush()
                        break  # only one img per article
                    else:
                        print(url)
                    '''
        except Exception as e:
            leftovers[a['_id']] = a['web_url']
            print(e, url)

    json.dump(month_data, open(data_root + 'nytimes_%d_%d.json' % (year, m), 'w'))
    json.dump(leftovers, open(data_root + 'leftovers_%d_%d.json' % (year, m), 'w'))


def main(num_pool, months):
    pool = ThreadPool(num_pool)
    leftovers = {}
    pool.map(retrieve_articles, months)
    pool.close()
    pool.join()
    json.dump(leftovers, open(root + "leftovers_%s.json" % year, 'w'))


if __name__ == '__main__':
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    h = HTMLParser()
    root = "./"
    data_root = root + "data/"
    g = Goose()

    # This is a special case since 2018 had only 6 months by the time the data was getting collected.
    # this year variable used in retrieve articles function

    # year = 2018
    # main(6, range(1, 7))

    num_pool = 12
    months = range(1, 13)
    years = range(2010, 2021)
    for y in years:
        year = y
        main(num_pool, months)
