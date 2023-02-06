# -*- coding: utf-8 -*-
import yaml
import sys
import os
from copy import deepcopy
from yaml_duplicate_exception import no_duplicates_constructor
import kote_exceptions

#возвращает список списков ['путь_до_схемы', 'блок', 'блок', ...]
def __list_from_dict_keys(parse_item):
    if isinstance(parse_item, str):

        return [[parse_item]]
    if not isinstance(parse_item, list):
        temp = []
        for keys, items in parse_item.iteritems():
            temp.append([{keys: items}])
        return __list_from_dict_keys([[parse_item]])
    ans = []
    for items in parse_item:
        if isinstance(items[0], dict):
            for keys in items[0]:
                temp = [items[0][keys], keys]
                if len(items) !=1:
                    temp1 = items[1:]
                    temp.extend(temp1)
                ans.extend(__list_from_dict_keys([temp]))
        else:
            ans.append(items)
    
    return ans


#функция возвращает список ключей со значениями-массивами
def __list_of_keys(params):
    keys = []
    if not isinstance(params, dict):
        raise kote_exceptions.BadType("We got type '{}', but need dict".format(type(params).__name__))

    for key, item in params.iteritems():
        if isinstance(item, list):
            keys.append(key)
    return keys


#функция для разделения списка, возвращает список словарей
def __separate_list(params, separate_key):
    ans = []
    for item in params[separate_key]:
        temp_dict = deepcopy(params)
        temp_dict[separate_key] = item
        ans.append(temp_dict)
    
    return ans


#функция для разделения всех списков, возвращает список словарей без списков на самом верхнем уровне
def __simple_parse(params):
    ans = [params]
    list_of_keys = __list_of_keys(params)
    for separate_key in list_of_keys:
        temp_ans = []
        for item in ans:
            temp_ans.extend(__separate_list(item, separate_key))
        ans = temp_ans

    return ans


#собирает из ямла все параметры и наследуется от шаблонов
def open_file(path):
    try:
        with open(path) as f:
            test = yaml.safe_load(f)
            try:
                if 'config' not in test:
                    # Для параметров клиента секция config может отсутствовать
                    test['config'] = {}
                while 'parent' in test['config']:
                    if not isinstance(test['config']['parent'], list):
                        with open(test['config']['parent']) as g:
                            template = yaml.safe_load(g)
                        del test['config']['parent']
                        test = templation(template, test)
                    else:
                        with open(test['config']['parent'][0]) as f:
                            template1 = yaml.safe_load(f)
                        for i in range(1, len(test['config']['parent'])):
                            with open(test['config']['parent'][i]) as g:
                                template2 = yaml.safe_load(g)
                            template1 = templation(template1, template2)
                        del test['config']['parent']
                        test = templation(template1, test)
            except Exception as e:
                test = [{'broken_test_marker': 1, 'test_path': path, 'text': str(e) + '(some problem with parent)'}]
                return test
    except Exception as e:
        test = [{'broken_test_marker': 1, 'test_path': path, 'text': str(e)}]
        return test
    test['config']['test_path'] = path
    test = smart_parse(test)

    return test


#очень крутая парсилка (правда)
def smart_parse(params):
    params_list = None
    try:
        params_list = [{'config': config} for config in __simple_parse(params['config'])]
    except kote_exceptions.BadType as e:
        # sys.exc_info()[2] want to use original trace
        raise kote_exceptions.BadYamlFormat(e, 'can not parse key config'), None, sys.exc_info()[2]

    if 'get_params' in params:
        temp_list = []
        for items in params_list:
            try:
                for parsed_get_params in __simple_parse(params['get_params']):
                    temp_items = deepcopy(items)
                    temp_items['get_params'] = deepcopy(parsed_get_params)
                    temp_list.append(temp_items)
            except kote_exceptions.BadType as e:
                # sys.exc_info()[2] want to use original trace
                raise kote_exceptions.BadYamlFormat(e, 'can not parse key get_params'), None, sys.exc_info()[2]
        params_list = temp_list
    if 'result' in params:
        for items in params_list:
            items['result'] = params['result']
    if 'schema' in params:
        for items in params_list:
            items['schema'] = __list_from_dict_keys(params['schema'])
    if 'meta' in params:
        for items in params_list:
            items['meta'] = params['meta']
    if 'exception' in params:
        for items in params_list:
            items['exception'] = params['exception']        

    return params_list


#шаблоны, потом доведу до ума 
def templation(template, test):
    for keys in test:
        if not keys in template:
            template[keys] = test[keys]
        else:
            for inner_keys in test[keys]:
                template[keys][inner_keys] = test[keys][inner_keys]
    return template


def get_params(path):
    # магия для вывода ошибки при дублировании ключей
    yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, no_duplicates_constructor, yaml.SafeLoader)

    if path == '':
        path = 'tests/kote/tests/'

    if os.path.isfile(path):
        if path.find('/clients/') == -1:
            filename = path.split('/')[-1]
            if not filename.startswith('test_'):
                print("\n{}".format("-" * 94))
                print('Warning')
                print('{}\nname should start with \'test_\''.format(path))
                print('Warning')
                print("-" * 94)
                # TODO why return magic symbol E? may be throw exception?
                return 'E'
        test = open_file(path)
        return test

    #тут запускаем самотесты
    elif path == 'self_test':
        params = []
        path = 'tests/kote/tests/framework_test'
        for root, dirs, files in os.walk(path):
            params = param_extension(root, files, params)
        return params

    elif not os.path.exists(path):
        raise kote_exceptions.PathNotFound(path)

    params = []
    for root, dirs, files in os.walk(path):
        if not '/framework_test' in root:
            params = param_extension(root, files, params)
    return params


def param_extension(root, files, params):
    if not '/examples' in root:
        for items in files:
            if not items.endswith('.yaml'):
                continue
            if root.find('/clients') == -1:
                if not items.startswith('test_'):
                    continue
            test = open_file(root + '/' + items)
            params.extend(test)
    return params
