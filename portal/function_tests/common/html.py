# -*- coding: utf-8 -*-
import json

from bs4 import BeautifulSoup


def get_page_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    page_info = soup.find('div', class_='page-info')
    if not page_info or not page_info.text:
        raise RuntimeError('No page info found in html')

    return json.loads(soup.find('div', class_='page-info').text)
