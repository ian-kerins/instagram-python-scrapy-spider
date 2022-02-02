# instagram-python-scrapy-spider
Instagram web scraping spider built with Python Scrapy. This scraper is designed to scrape the following data from every post on a user's account:

* Post URL
* Image URL or Video URL
* Post Captions
* Date Posted
* Number of Likes
* Number of Comments

In this Instagram scraper, we're going to use:

- [Scraper API](https://www.scraperapi.com/) as our proxy solution, as Instagram has pretty aggressive anti-scraping in place. You can sign up to a [free account here](https://dashboard.scraperapi.com/signup) which will give you 5,000 free requests.  
- [ScrapeOps](https://scrapeops.io/) to monitor our scrapers for free and alert us if they run into trouble. **Live demo here:** [ScrapeOps Demo](https://scrapeops.io/app/login/demo)

![ScrapeOps Dashboard](https://scrapeops.io/assets/images/scrapeops-promo-286a59166d9f41db1c195f619aa36a06.png)

## Using the Instagram Spider
Make sure Scrapy is installed:

```
pip install scrapy
```

Set the Instagram accounts you want to scrape, in the `instagram.py` spider file.

```
user_accounts = ['nike', 'adidas'] 
```

### Setting Up ScraperAPI
Signup to [Scraper API](https://www.scraperapi.com/signup) and get your free API key that allows you to scrape 1,000 pages per month for free. Enter your API key into the API variable:

```
API = ‘<YOUR_API_KEY>’

def get_url(url):
    payload = {'api_key': API, 'url': url}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

```

By default, the spider is set to have a max concurrency of 5 concurrent requests as this the max concurrency allowed on Scraper APIs free plan. If you have a plan with higher concurrency then make sure to increase the max concurrency in the `settings.py`.

```
## settings.py

CONCURRENT_REQUESTS = 5
RETRY_TIMES = 5

# DOWNLOAD_DELAY
# RANDOMIZE_DOWNLOAD_DELAY
```
We should also set `RETRY_TIMES` to tell Scrapy to retry any failed requests (to 5 for example) and make sure that `DOWNLOAD_DELAY`  and `RANDOMIZE_DOWNLOAD_DELAY` aren’t enabled as these will lower your concurrency and are not needed with Scraper API.

### Integrating ScrapeOps
[ScrapeOps](https://scrapeops.io/) is already integrated into the scraper via the `settings.py` file. However, to use it you must:

Install the [ScrapeOps Scrapy SDK](https://github.com/ScrapeOps/scrapeops-scrapy-sdk) on your machine.

```
pip install scrapeops-scrapy
```

And sign up for a [free ScrapeOps account here](https://scrapeops.io/app/register) so you can insert your **API Key** into the `settings.py` file:

```
    ## settings.py
    
    ## Add Your ScrapeOps API key
    SCRAPEOPS_API_KEY = 'YOUR_API_KEY'
    
    ## Add In The ScrapeOps Extension
    EXTENSIONS = {
     'scrapeops_scrapy.extension.ScrapeOpsMonitor': 500, 
    }
    
    ## Update The Download Middlewares
    DOWNLOADER_MIDDLEWARES = { 
	'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550, 
	'scrapy.downloadermiddlewares.retry.RetryMiddleware': None, 
    }
```
From there, our scraping stats will be automatically logged and automatically shipped to our dashboard.

### Running The Spider
To run the spider, use:

```
scrapy crawl instagram -o test.csv
```
