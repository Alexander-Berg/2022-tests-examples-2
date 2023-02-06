from datetime import datetime, timedelta
import hashlib
import json


def to_bytes(value, encoding='utf-8', raise_exception=True, label=None):
    """Аргумент label может быть использован для отладки. Когда ты в нескольких
       местах добавляешь вызовы to_bytes, а потом загрузчик на каком-то из них падает
       с ошибкой типа:

       TypeError: Unsupported argument type: <class 'NoneType'>

       то невозможно понять, в каком месте проблема - по стеку этого не видно если
       функция вызывалась где-то внутри nile.
       В таких случаях можно пометить вызовы to_bytes, и логи будут содержать
       дополнительную информацию:

       TypeError: Unsupported argument type: <class 'NoneType'> (label=normalize_car_number)

       Указывать label совместно с raise_exception=False - не имеет смысла.
    """
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode(encoding)

    if raise_exception:
        msg = 'Unsupported argument type: {}'.format(type(value))
        if label is not None:
            msg += ' (label={})'.format(label)
        raise TypeError(msg)
    else:
        return value


def get_md5(val):
    v = hashlib.md5(to_bytes(str(val) + '.._..')).hexdigest()

    return '{}-{}-{}-{}-{}'.format(v[:8], v[8:12], v[12:16], v[16:20], v[20:])


oktell = 1

created_field = [
    {'type': 'created_field.json',
     'tests': [
         {
             'source':
                 [dict(id=1, value='a', business_dt=datetime(2020, 4, 3), created_dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  ],
             'val':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 3), val='a'),
                  ]
         },
         {
             'source':
                 [dict(id=1, value='z', business_dt=datetime(2020, 3, 1), created_dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  ],
             'val':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 3), val='a'),
                  ]
         },
         {
             'source':
                 [dict(id=1, value='x', business_dt=datetime(2020, 4, 4), created_dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  ],
             'val':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 4), val='x'),
                  ]
         },
     ]
     },
    {'type': 'attr_created_and_extend.json',
     'tests': [
         {
             'source':
                 [dict(id=1, value='a', business_dt=datetime(2020, 4, 3), created_dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  ],
             'val':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 3), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), val='a'),
                  dict(_source_id=-1, id=get_md5(1), utc_valid_from_dttm=datetime(1970, 1, 1), utc_valid_to_dttm=datetime(2020, 4, 2, 23, 59, 59), val='a'),
                  ]
         },
         {
             'source':
                 [dict(id=1, value='b', business_dt=datetime(2020, 4, 4), created_dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  ],
             'val':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 3), utc_valid_to_dttm=datetime(2020, 4, 3, 23, 59, 59), val='a'),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 4), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), val='b'),
                  dict(_source_id=-1, id=get_md5(1), utc_valid_from_dttm=datetime(1970, 1, 1), utc_valid_to_dttm=datetime(2020, 4, 2, 23, 59, 59), val='a'),
                  ]
         },
         {
             'source':
                 [dict(id=1, value='c', business_dt=datetime(2020, 4, 1), created_dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  ],
             'val':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 1), utc_valid_to_dttm=datetime(2020, 4, 2, 23, 59, 59), val='c'),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 3), utc_valid_to_dttm=datetime(2020, 4, 3, 23, 59, 59), val='a'),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 4), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), val='b'),
                  dict(_source_id=-1, id=get_md5(1), utc_valid_from_dttm=datetime(1970, 1, 1), utc_valid_to_dttm=datetime(2020, 3, 31, 23, 59, 59), val='c'),
                  ]
         },
         {
             'source':
                 [dict(id=1, value='q', business_dt=datetime(1970, 1, 1), created_dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(1970, 1, 1)),
                  ],
             'val':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 1), utc_valid_to_dttm=datetime(2020, 4, 2, 23, 59, 59), val='c'),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 3), utc_valid_to_dttm=datetime(2020, 4, 3, 23, 59, 59), val='a'),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 4), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), val='b'),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(1970, 1, 1), utc_valid_to_dttm=datetime(2020, 3, 31, 23, 59, 59), val='q'),
                  ]
         },
         {
             'source':
                 [dict(id=1, value='e', business_dt=datetime(2020, 3, 1), created_dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(1970, 1, 1)),
                  ],
             'val':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 3, 1), utc_valid_to_dttm=datetime(2020, 3, 31, 23, 59, 59), val='e'),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 1), utc_valid_to_dttm=datetime(2020, 4, 2, 23, 59, 59), val='c'),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 3), utc_valid_to_dttm=datetime(2020, 4, 3, 23, 59, 59), val='a'),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 4, 4), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), val='b'),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(1970, 1, 1), utc_valid_to_dttm=datetime(2020, 2, 29, 23, 59, 59), val='q'),
                  ]
         },
     ]
     },
]


def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()


if __name__ == '__main__':
    for ent in created_field:
        f = open(ent['type'], "w")
        f.write(json.dumps(ent['tests'], default=myconverter))
        f.close()
