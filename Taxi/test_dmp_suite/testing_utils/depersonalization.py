import re
import hashlib

from typing import Union, List, Tuple


class KeyValueChecker(object):
    def __init__(self, key_filters, value_filters):
        self.key_filters = key_filters
        self.value_filters = value_filters

    def match(self, k, v):
        for key_filter in self.key_filters:
            if key_filter(k):
                for value_filter in self.value_filters:
                    if value_filter(v):
                        return True
        return False


class Depersonalization(object):
    matchers = [
        KeyValueChecker(
            key_filters=[
                re.compile('.*phone$').match,
                re.compile('^phone_number$').match
            ],
            value_filters=[
                re.compile(r'\+[\d \-]+$').match]
        ),
        KeyValueChecker(
            key_filters=[
                lambda k: k in ('name', 'driver_license_normalized', 'driver_license', 'apikey')
            ],
            value_filters=[lambda v: v]
        ),
        KeyValueChecker(
            key_filters=[
                lambda n: 'email' in n,
            ],
            value_filters=[lambda v: v]
        )
    ]
    salt = '7b1821e6-35c5-494c-be00-708f76e29904'

    def uglify(self, val):
        return hashlib.md5((self.salt + val).encode('utf-8')).hexdigest()[:len(val)]

    def replace_inplace(self, data):  # type: (Union[List, dict]) -> Tuple[Union[List, dict], bool]
        replaced = False
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, list):
                    item, lc_replaced = self.replace_inplace(item)
                elif isinstance(item, dict):
                    item, lc_replaced = self.replace_inplace(item)
                else:
                    continue
                if lc_replaced:
                    data[i] = item
                    replaced = True
        elif isinstance(data, dict):
            for k, v in data.items():

                if isinstance(v, (list, dict)):
                    v, lc_replaced = self.replace_inplace(v)
                    if lc_replaced:
                        data[k] = v
                        replaced = True

                if isinstance(v, str):
                    for for_uglify in self.matchers:
                        if for_uglify.match(k, v):
                            data[k] = self.uglify(v)
                            replaced = True
        else:
            raise ValueError('wrong data type {}'.format(type(data)))
        return data, replaced
