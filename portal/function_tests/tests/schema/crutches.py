# -*- coding: utf-8 -*-
from common.utils  import delete

# если хотите добавить сюда костыль, заведите тикет с описанием
# и добавьте функцию с именем, содержащим очередь и номер тикета

def crutch_HOME_71234(response):
    if not isinstance(response, dict):
        return
    if 'block' not in response or not isinstance(response['block'], list):
        return

    i = 0
    block = response['block']
    while i < len(block):
        if not isinstance(block[i], dict):
            continue

        if 'data' in block[i] and isinstance(block[i]['data'], dict):
            delete(block[i]['data'], 'show')

        if block[i].get('id') in ['search']:
            del block[i]
        else:
            i += 1


def crutch_HOME_68807(block):
    if 'data' in block and not 'data_url' in block['data']:
        block['data']['data_url'] = 'https://fake.url'


def crutch_HOME_68803(response):
    if 'extension_block' in response and 'zen_extensions' in response['extension_block']:
        for extension in response['extension_block']['zen_extensions']:
            delete(extension, 'block')
            delete(extension, 'heavy_id')


def crutch_HOME_68785(response):
    if 'welcome_tab' in response and 'allowed_time_intervals' in response['welcome_tab']:
        for interval in response['welcome_tab']['allowed_time_intervals']:
            interval['max_time_of_day'] = int(interval['max_time_of_day'])
            interval['min_time_of_day'] = int(interval['min_time_of_day'])


def crutch_HOME_68712_1(block):
    if 'data' in block and 'tab' in block['data']:
        for data in block['data']['tab']:
            if 'program' in data:
                for program in data['program']:
                    delete(program, 'program_id')
                    delete(program, 'event_id')


def crutch_HOME_68712_2(response):
    if 'nav_panel' in response and 'rounded_design' in response['nav_panel']:
        if response['nav_panel']['rounded_design'] == 0:
            response['nav_panel']['rounded_design'] = False
        elif response['nav_panel']['rounded_design'] == 1:
            response['nav_panel']['rounded_design'] = True


def crutch_HOME_70251(block):
    if block.get('data'):
        delete(block['data'], 'city_locative')


def crutch_HOME_71272(block):
    if block.get('data'):
        delete(block['data'], 'wind_direction')