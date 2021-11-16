import json
import shutil

original_path = '../../data/images/'

categories = {'politics', 'business', 'opinion', 'technology', 'science', 'health', 'sports', 'arts', 'theater',
              'books', 'dining', 'travel', 'movies', 'fashion', 'realestate'}


def build_json_name(year, month):
    return './data/nytimes_' + str(year) + '_' + str(month) + '.json'


def build_img_path(img_name):
    return './images/' + img_name + '.jpg', original_path + img_name + '.jpg'


def extract_category(url):
    urls = url.split('/')
    category = urls[6]
    if category == 'us':
        category = urls[7]
    return category


categories_news = {}

for year in range(2010, 2021):
    for month in range(1, 13):
        json_file = build_json_name(year, month)
        print(json_file)
        j = json.load(open(json_file, 'r'))
        for news_name in j:
            data = j[news_name]
            headline = data['headline']['main']
            article_url = data['article_url']
            article = data['article']
            abstract = data['abstract']
            article_id = data['article_id']
            img = data['image']
            caption = data['caption']

            try:
                category = extract_category(article_url)
                if category in categories:
                    if category not in categories_news:
                        categories_news[category] = {}
                    if headline is not None:
                        data['headline'] = headline
                        data['category'] = category
                        categories_news[category][news_name] = data
                        # copy img
                        dst_path, src_path = build_img_path(news_name)
                        shutil.copyfile(src=src_path, dst=dst_path)

            except Exception as e:
                print('error')
                continue

for category in categories_news:
    category_news = categories_news[category]
    json.dump(category_news, open('./categories/' + str(category), 'w'))
    print(category, len(category_news.keys()))
