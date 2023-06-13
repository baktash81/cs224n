from pathlib import Path

import scrapy
import json
import jmespath
import pandas as pd
from collections import defaultdict


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'linketo pechepoun inja',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            # yield scrapy.Request(url=url, callback=self.parse_post)
            

    def parse(self, response):
        self.parse_post(response)
        page = response.url.split("/")[-2]
        filename = f'quotes-{page}.html'
        Path(filename).write_bytes(response.body)
        self.log(f'Saved file {filename}')


    def parse_post(self, response):
        """
        Parses a post page
        """
        if len(response.css(
                '.dl-box')) > 1:  # our spider does not support such pages with multiple music tracks like https://tinyurl.com/2p85b4hx
            return []
        # file = open("file.csv",'w')
        dicts = defaultdict(lambda :list())
        schema_graph_data = json.loads(response.xpath('//script[@type="application/ld+json"]//text()').get())
        info = jmespath.search('"@graph"[?"@type"==\'Article\']|[0]', schema_graph_data)
        if info:
            songs = response.xpath('//ul[has-class("audioplayer-audios")]//li')
            artists = response.xpath('//div[has-class("AR-Si")]//a')
            for song in songs:
                music_name = song.attrib.get('data-title', '')
                album_name = song.attrib.get('data-album', '')
                artist_name =  song.attrib.get('data-artist', '')
                file_urls = song.attrib.get('data-src', '')
                
                dicts["Music-Name : "].append(music_name)
                dicts["Album-Name : "].append(album_name)
                dicts["Artist-Name : "].append(artist_name)
                dicts["file-urls : "].append(file_urls)

            print(dicts)
            df = pd.DataFrame.from_dict(dicts)
            df.to_csv('./file.csv')


