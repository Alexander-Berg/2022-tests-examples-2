import re
import os
import pytz
import yaml
import pytest

@pytest.mark.parametrize('path_to_object',
                         [('/doc/api/models/store.yaml', 'Store'),
                          ('/doc/api/models/cluster.yaml', 'Cluster')])
async def test_check_timezone(tap, path_to_object):
    with tap:
        tmp = os.path.abspath(os.getcwd())
        path = tmp + path_to_object[0]
        with open(path, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader) #конфиги магазина
        s = data['components']['schemas'][path_to_object[1]]
        s = s['properties']['tz']['pattern']
        pattern = r'{}'.format(s)
        cnt = 0
        for tz in pytz.all_timezones:
            match = re.search(pattern, str(tz))
            if match is not None:
                cnt += 1
        tap.eq(cnt, len(pytz.all_timezones), 'Регулярка все зоны обрабатывает')
