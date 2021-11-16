# CrawlNYT
 
With those code you can collect Multimodal New York Times by your self.

We borrowed some code from furkanbiten/[GoodNews](https://github.com/furkanbiten/GoodNews). Thanks a lot!

## Environment

Python 3

## Steps

1. First, you need to apply a NYT developer account and get a api key and fill it into retrieve_all_urls.py in folder get_data/with_api/.
2. Then you can use retrieve_all_url.py to crawl the multimodal news' meta information.
3. With those meta information, then you can use get_data_api.py to crawl the actual news.
4. In step 3 you will obtain all the NYT news in target years. And if you want to select specific news categories, you can use 
get_category_image_text.py.


## Attention

There still exist some hard-coded folder address in the code, and need to be  modified manually.
This will be fixed later.
