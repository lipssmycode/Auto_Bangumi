# -*- coding: UTF-8 -*-
import sys
import time
import requests
from bs4 import BeautifulSoup
import json
import re


class CollectRSS:
    def __init__(self, config, info):
        self.info = info
        self.config = config
        self.bangumi_title = []

    def collect_info(self):
        episode_rules = [r'(.*)\[(\d{1,3}|\d{1,3}\.\d{1,2})(?:v\d{1,2})?(?:END)?\](.*)',
                         r'(.*)\[E(\d{1,3}|\d{1,3}\.\d{1,2})(?:v\d{1,2})?(?:END)?\](.*)',
                         r'(.*)\[第(\d*\.*\d*)话(?:END)?\](.*)',
                         r'(.*)\[第(\d*\.*\d*)話(?:END)?\](.*)',
                         r'(.*)第(\d*\.*\d*)话(?:END)?(.*)',
                         r'(.*)第(\d*\.*\d*)話(?:END)?(.*)',
                         r'(.*)- (\d{1,3}|\d{1,3}\.\d{1,2})(?:v\d{1,2})?(?:END)? (.*)']
        url = self.config["rss_link"]
        rss = requests.get(url, 'utf-8')
        soup = BeautifulSoup(rss.text, 'xml')
        item = soup.find_all('item')
        for a in item:
            name = a.title.string
            pattern = r'\[|\]|\u3010|\u3011|\★|\*|\(|\)|\（|\）|\_'
            for i in range(2):
                n = re.split(pattern, name)
                try:
                    if re.search("\d{2,3}^月", n[1]) is None:
                        name = re.sub(f'\[{n[1]}\]|【{n[1]}】|★{n[1]}★', '', name).strip()
                    else:
                        break
                except IndexError:
                    break
            for rule in episode_rules:
                match_obj = re.match(rule, name, re.I)
                if match_obj is not None:
                    new_name = re.sub(r'\[|\]', '', f'{match_obj.group(1)}')
                    new_name = re.split(r'/', new_name)[-1].strip()
                    if new_name not in self.bangumi_title:
                        self.bangumi_title.append(new_name)

    def write_info(self):
        bangumi_info = self.info
        had_data = []
        for data in bangumi_info:
            had_data.append(data["title"])
        for title in self.bangumi_title:
            a = re.match(r'(.*)(S.\d)', title, re.I)
            if a is not None:
                title = a.group(1).strip()
                season = a.group(2).strip()
            else:
                season = ''
            if title not in had_data:
                bangumi_info.append({
                    "title": title,
                    "season": season
                })
                sys.stdout.write(f"[{time.strftime('%X')}]  add {title} {season}" + "\n")
                sys.stdout.flush()
        # 写入数据
        with open("/config/bangumi.json", 'w', encoding='utf8') as f:
            json.dump(bangumi_info, f, indent=4, separators=(',', ': '), ensure_ascii=False)

    def run(self):
        sys.stdout.write(f"[{time.strftime('%X')}]  Start scanning RSS Feed." + "\n")
        sys.stdout.flush()
        self.collect_info()
        self.write_info()
        sys.stdout.write(f"[{time.strftime('%X')}]  Finished." + "\n")
        sys.stdout.flush()