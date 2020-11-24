# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode
import json
from datetime import datetime
API = 'YOURAPIKEY'
user_accounts = ['nike', 'adidas'] 


def get_url(url):
    payload = {'api_key': API, 'url': url}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['api.scraperapi.com']
    custom_settings = {'CONCURRENT_REQUESTS_PER_DOMAIN': 5}

    def start_requests(self):
        for username in user_accounts:
            url = f'https://www.instagram.com/{username}/?hl=en'
            yield scrapy.Request(get_url(url), callback=self.parse)

    def parse(self, response):
        x = response.xpath("//script[starts-with(.,'window._sharedData')]/text()").extract_first()
        json_string = x.strip().split('= ')[1][:-1]
        data = json.loads(json_string)
        # all that we have to do here is to parse the JSON we have
        user_id = data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        next_page_bool = \
            data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['page_info'][
                'has_next_page']
        edges = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_felix_video_timeline']['edges']
        for i in edges:
            url = 'https://www.instagram.com/p/' + i['node']['shortcode']
            video = i['node']['is_video']
            date_posted_timestamp = i['node']['taken_at_timestamp']
            date_posted_human = datetime.fromtimestamp(date_posted_timestamp).strftime("%d/%m/%Y %H:%M:%S")
            like_count = i['node']['edge_media_preview_like']['count'] if "edge_media_preview_like" in i['node'].keys() else ''
            comment_count = i['node']['edge_media_to_comment']['count'] if 'edge_media_to_comment' in i[
                'node'].keys() else ''
            captions = ""
            if i['node']['edge_media_to_caption']:
                for i2 in i['node']['edge_media_to_caption']['edges']:
                    captions += i2['node']['text'] + "\n"

            if video:
                image_url = i['node']['display_url']
            else:
                image_url = i['node']['thumbnail_resources'][-1]['src']
            item = {'postURL': url, 'isVideo': video, 'date_posted': date_posted_human,
                    'timestamp': date_posted_timestamp, 'likeCount': like_count, 'commentCount': comment_count, 'image_url': image_url,
                    'captions': captions[:-1]}
            if video:
                yield scrapy.Request(get_url(url), callback=self.get_video, meta={'item': item})
            else:
                item['videoURL'] = ''
                yield item
        if next_page_bool:
            cursor = \
                data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['page_info'][
                    'end_cursor']
            di = {'id': user_id, 'first': 12, 'after': cursor}
            print(di)
            params = {'query_hash': 'e769aa130647d2354c40ea6a439bfc08', 'variables': json.dumps(di)}
            url = 'https://www.instagram.com/graphql/query/?' + urlencode(params)
            yield scrapy.Request(get_url(url), callback=self.parse_pages, meta={'pages_di': di})

    def parse_pages(self, response):
        di = response.meta['pages_di']
        data = json.loads(response.text)
        for i in data['data']['user']['edge_owner_to_timeline_media']['edges']:
            video = i['node']['is_video']
            url = 'https://www.instagram.com/p/' + i['node']['shortcode']
            if video:
                image_url = i['node']['display_url']
                video_url = i['node']['video_url']
            else:
                video_url = ''
                image_url = i['node']['thumbnail_resources'][-1]['src']
            date_posted_timestamp = i['node']['taken_at_timestamp']
            captions = ""
            if i['node']['edge_media_to_caption']:
                for i2 in i['node']['edge_media_to_caption']['edges']:
                    captions += i2['node']['text'] + "\n"
            comment_count = i['node']['edge_media_to_comment']['count'] if 'edge_media_to_comment' in i['node'].keys() else ''
            date_posted_human = datetime.fromtimestamp(date_posted_timestamp).strftime("%d/%m/%Y %H:%M:%S")
            like_count = i['node']['edge_media_preview_like']['count'] if "edge_media_preview_like" in i['node'].keys() else ''
            item = {'postURL': url, 'isVideo': video, 'date_posted': date_posted_human,
                    'timestamp': date_posted_timestamp, 'likeCount': like_count, 'commentCount': comment_count,
                    'image_url': image_url,
                    'videoURL': video_url, 'captions': captions[:-1]}
            yield item
        next_page_bool = data['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
        if next_page_bool:
            cursor = data['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
            di['after'] = cursor
            params = {'query_hash': 'e769aa130647d2354c40ea6a439bfc08', 'variables': json.dumps(di)}
            url = 'https://www.instagram.com/graphql/query/?' + urlencode(params)
            yield scrapy.Request(get_url(url), callback=self.parse_pages, meta={'pages_di': di})

    def get_video(self, response):
        # only from the first page
        item = response.meta['item']
        video_url = response.xpath('//meta[@property="og:video"]/@content').extract_first()
        item['videoURL'] = video_url
        yield item
