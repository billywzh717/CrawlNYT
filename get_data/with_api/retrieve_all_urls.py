
from urllib.request import urlopen
import tqdm
import json
import time

def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.items()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, str):
        return input.encode('utf-8')
    else:
        return input


hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

api_key = "p5fE1Dmkldn74XKJrzRkv0sH5ddxurA1"
monthly = "http://api.nytimes.com/svc/archive/v1/%s/%s.json?api-key=%s"
years = range(2010, 2021)
months = range(1, 13)
root = "."

for y in tqdm.tqdm(years):
    for m in months:
        request_string = monthly % (y, m, api_key)
        response = urlopen(request_string)
        content = bytes.decode(response.read())
        if content:
            articles = convert(json.loads(content))
        with open('./api/nyarticles_%s_%s.json' % (y, m), 'w', encoding='utf8') as fr:
            fr.write(content)
        print('./api/nyarticles_%s_%s.json' % (y, m))
        time.sleep(10)
        # json.dump(articles, open('./api/nyarticles_%s_%s.json' % (y, m), 'w'))
