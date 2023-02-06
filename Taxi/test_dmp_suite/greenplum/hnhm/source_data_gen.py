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


params1 = [
    {'type': 'attr_update.json',
     'tests': [
         {
             'source':
                 [dict(id=1, value='a', dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='b', dt=datetime(2019, 3, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), edt=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a'),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b')
                  ]
         },
         {
             'source':
                 [dict(id=1, value='aa', dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='bb', dt=datetime(2019, 3, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), edt=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='aa'),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='bb')
                  ],
         },
         {
             'source':
                 [dict(id=1, value='cc', dt=datetime(2019, 2, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='dd', dt=datetime(2019, 4, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 2, 1), edt=datetime(2019, 2, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 4, 1), edt=datetime(2019, 4, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 2, 1), evalue='cc'),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 4, 1), evalue='dd')
                  ],
         },
         {
             'source':
                 [dict(id=1, value='c', dt=datetime(2018, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='d', dt=datetime(2018, 3, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 2, 1), edt=datetime(2019, 2, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 4, 1), edt=datetime(2019, 4, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 2, 1), evalue='cc'),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 4, 1), evalue='dd')
                  ],
         }
     ]
     },
    {'type': 'attr_ignore.json',
     'tests': [
         {
             'source':
                 [dict(id=1, value='a', dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='b', dt=datetime(2019, 3, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), edt=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a'),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b')
                  ]
         },
         {
             'source':
                 [dict(id=1, value='aa', dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='bb', dt=datetime(2019, 3, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), edt=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a'),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b')
                  ],
         },
         {
             'source':
                 [dict(id=1, value='a', dt=datetime(2018, 10, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='b', dt=datetime(2018, 11, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 10, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 11, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 10, 1), edt=datetime(2018, 10, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 11, 1), edt=datetime(2018, 11, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a'),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b')
                  ],
         },
         {
             'source':
                 [dict(id=1, value='a', dt=datetime(2018, 5, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='b', dt=datetime(2018, 6, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 5, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 5, 1), edt=datetime(2018, 5, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 1), edt=datetime(2018, 6, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a'),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b')
                  ],
         },
         {
             'source':
                 [dict(id=1, value='c', dt=datetime(2017, 5, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='d', dt=datetime(2017, 6, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2017, 5, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2017, 6, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2017, 5, 1), edt=datetime(2017, 5, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2017, 6, 1), edt=datetime(2017, 6, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2017, 5, 1), evalue='c'),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2017, 6, 1), evalue='d')
                  ],
         }
     ]
     },
    {'type': 'attr_new.json',
     'tests': [
         {
             'source':
                 [dict(id=1, value='a', dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='b', dt=datetime(2019, 3, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), edt=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ]
         },
         {
             'source':
                 [dict(id=1, value='aa', dt=datetime(2019, 1, 2), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='bb', dt=datetime(2019, 3, 2), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), edt=datetime(2019, 3, 2))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue='aa',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), evalue='bb',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=1, value='aaa', dt=datetime(2018, 1, 2), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='bbb', dt=datetime(2018, 3, 2), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), edt=datetime(2019, 3, 2))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2), evalue='aaa',
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue='aa',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2), evalue='bbb',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), evalue='bb',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=1, value='aaaa', dt=datetime(2018, 4, 2), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='bbbb', dt=datetime(2018, 6, 2), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), edt=datetime(2019, 3, 2))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2), evalue='aaa',
                       utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2), evalue='aaaa',
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue='aa',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2), evalue='bbb',
                       utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2), evalue='bbbb',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), evalue='bb',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=1, value='cccc', dt=datetime(2018, 4, 2), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='dddd', dt=datetime(2018, 6, 2), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), edt=datetime(2019, 3, 2))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2), evalue='aaa',
                       utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2), evalue='cccc',
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue='aa',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2), evalue='bbb',
                       utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2), evalue='dddd',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), evalue='bb',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=3, value='c', dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, value='cc', dt=datetime(2019, 3, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), edt=datetime(2019, 3, 2)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1), edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), eid=3)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2), evalue='aaa',
                       utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2), evalue='cccc',
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue='aa',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2), evalue='bbb',
                       utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2), evalue='dddd',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), evalue='bb',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='c',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='cc',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=3, value='d', dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, value='ccc', dt=datetime(2019, 2, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), edt=datetime(2019, 3, 2)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1), edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), eid=3)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2), evalue='aaa',
                       utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2), evalue='cccc',
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue='aa',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2), evalue='bbb',
                       utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2), evalue='dddd',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), evalue='bb',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='d',
                       utc_valid_to_dttm=datetime(2019, 1, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 1), evalue='ccc',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='cc',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=3, value='e', dt=datetime(2019, 1, 10), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, value='f', dt=datetime(2019, 2, 10), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), edt=datetime(2019, 3, 2)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1), edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), eid=3)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2), evalue='aaa',
                       utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2), evalue='cccc',
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue='aa',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2), evalue='bbb',
                       utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2), evalue='dddd',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), evalue='bb',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='d',
                       utc_valid_to_dttm=datetime(2019, 1, 9, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 10), evalue='e',
                       utc_valid_to_dttm=datetime(2019, 1, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 1), evalue='ccc',
                       utc_valid_to_dttm=datetime(2019, 2, 9, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 10), evalue='f',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='cc',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=3, value='z', dt=datetime(2019, 1, 10), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, value='rr', dt=datetime(2019, 2, 5), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, value='rr1', dt=datetime(2019, 2, 7), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, value='rr2', dt=datetime(2019, 4, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), edt=datetime(2019, 3, 2)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 4, 1), edt=datetime(2019, 4, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), eid=3)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2), evalue='aaa',
                       utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2), evalue='cccc',
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue='aa',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2), evalue='bbb',
                       utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2), evalue='dddd',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), evalue='bb',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='d',
                       utc_valid_to_dttm=datetime(2019, 1, 9, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 10), evalue='z',
                       utc_valid_to_dttm=datetime(2019, 1, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 1), evalue='ccc',
                       utc_valid_to_dttm=datetime(2019, 2, 4, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 5), evalue='rr',
                       utc_valid_to_dttm=datetime(2019, 2, 6, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 7), evalue='rr1',
                       utc_valid_to_dttm=datetime(2019, 2, 9, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 10), evalue='f',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='cc',
                       utc_valid_to_dttm=datetime(2019, 3, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 4, 1), evalue='rr2',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=3, value='tt', dt=datetime(2018, 1, 10), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, value='pp', dt=datetime(2018, 2, 5), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2018, 1, 10))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), edt=datetime(2019, 3, 2)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 4, 1), edt=datetime(2019, 4, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), eid=3)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2), evalue='aaa',
                       utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2), evalue='cccc',
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue='aa',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),

                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2), evalue='bbb',
                       utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2), evalue='dddd',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), evalue='bb',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),

                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2018, 1, 10), evalue='tt',
                       utc_valid_to_dttm=datetime(2018, 2, 4, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2018, 2, 5), evalue='pp',
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='d',
                       utc_valid_to_dttm=datetime(2019, 1, 9, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 10), evalue='z',
                       utc_valid_to_dttm=datetime(2019, 1, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 1), evalue='ccc',
                       utc_valid_to_dttm=datetime(2019, 2, 4, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 5), evalue='rr',
                       utc_valid_to_dttm=datetime(2019, 2, 6, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 7), evalue='rr1',
                       utc_valid_to_dttm=datetime(2019, 2, 9, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 10), evalue='f',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='cc',
                       utc_valid_to_dttm=datetime(2019, 3, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 4, 1), evalue='rr2',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=3, value='ccc', dt=datetime(2019, 1, 5), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, value='ccc', dt=datetime(2019, 2, 3), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2018, 1, 10))
                  ],
             'edt':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), edt=datetime(2019, 3, 2)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 4, 1), edt=datetime(2019, 4, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), eid=2),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), eid=3)
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2), evalue='aaa',
                       utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2), evalue='cccc',
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue='aa',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),

                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2), evalue='bbb',
                       utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2), evalue='dddd',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2), evalue='bb',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),

                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2018, 1, 10), evalue='tt',
                       utc_valid_to_dttm=datetime(2018, 2, 4, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2018, 2, 5), evalue='pp',
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='d',
                       utc_valid_to_dttm=datetime(2019, 1, 4, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 5), evalue='ccc',
                       utc_valid_to_dttm=datetime(2019, 1, 9, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 10), evalue='z',
                       utc_valid_to_dttm=datetime(2019, 1, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 1), evalue='ccc',
                       utc_valid_to_dttm=datetime(2019, 2, 4, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 5), evalue='rr',
                       utc_valid_to_dttm=datetime(2019, 2, 6, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 7), evalue='rr1',
                       utc_valid_to_dttm=datetime(2019, 2, 9, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 10), evalue='f',
                       utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1), evalue='cc',
                       utc_valid_to_dttm=datetime(2019, 3, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(3), utc_valid_from_dttm=datetime(2019, 4, 1), evalue='rr2',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         }
     ]
     },
    {'type': 'attr_update_partition.json',
     'tests': [
         {
             'source':
                 [dict(id=1, value='a', dt=datetime(2019, 1, 1), pdt=datetime(2019, 1, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='b', dt=datetime(2019, 3, 1), pdt=datetime(2019, 1, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       edt=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a'),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b')
                  ]
         },
         {
             'source':
                 [dict(id=1, value='aa', dt=datetime(2019, 1, 1), pdt=datetime(2019, 1, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='bb', dt=datetime(2019, 3, 1), pdt=datetime(2019, 1, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       edt=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='aa'),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='bb')
                  ],
         },
         {
             'source':
                 [dict(id=1, value='cc', dt=datetime(2019, 2, 1), pdt=datetime(2019, 1, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='dd', dt=datetime(2019, 4, 1), pdt=datetime(2019, 1, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 2, 1),
                       edt=datetime(2019, 2, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 4, 1),
                       edt=datetime(2019, 4, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 2, 1),
                       evalue='cc'),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 4, 1),
                       evalue='dd')
                  ],
         },
         {
             'source':
                 [dict(id=1, value='c', dt=datetime(2018, 1, 1), pdt=datetime(2019, 1, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='d', dt=datetime(2018, 3, 1), pdt=datetime(2019, 1, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 2, 1),
                       edt=datetime(2019, 2, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 4, 1),
                       edt=datetime(2019, 4, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 2, 1),
                       evalue='cc'),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 4, 1),
                       evalue='dd')
                  ],
         },
         {
             'source':
                 [dict(id=1, value='cc', dt=datetime(2019, 2, 1), pdt=datetime(2019, 2, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='dd', dt=datetime(2019, 4, 1), pdt=datetime(2019, 2, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 2, 1),
                       edt=datetime(2019, 2, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 4, 1),
                       edt=datetime(2019, 4, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 2, 1),
                       evalue='cc'),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 4, 1),
                       evalue='dd')
                  ],
         }
     ]
     },
    {'type': 'attr_ignore_partition.json',
     'tests': [
         {
             'source':
                 [dict(id=1, pdt=datetime(2019, 1, 1), value='a', dt=datetime(2019, 1, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, pdt=datetime(2019, 1, 1), value='b', dt=datetime(2019, 3, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       edt=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a'),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b')
                  ]
         },
         {
             'source':
                 [dict(id=1, pdt=datetime(2019, 1, 1), value='aa', dt=datetime(2019, 1, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, pdt=datetime(2019, 1, 1), value='bb', dt=datetime(2019, 3, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       edt=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a'),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b')
                  ],
         },
         {
             'source':
                 [dict(id=1, pdt=datetime(2019, 1, 1), value='a', dt=datetime(2018, 10, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, pdt=datetime(2019, 1, 1), value='b', dt=datetime(2018, 11, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 10, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 11, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 10, 1),
                       edt=datetime(2018, 10, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 11, 1),
                       edt=datetime(2018, 11, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a'),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b')
                  ],
         },
         {
             'source':
                 [dict(id=1, pdt=datetime(2019, 1, 1), value='a', dt=datetime(2018, 5, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, pdt=datetime(2019, 1, 1), value='b', dt=datetime(2018, 6, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 5, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 5, 1),
                       edt=datetime(2018, 5, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 1),
                       edt=datetime(2018, 6, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a'),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b')
                  ],
         },
         {
             'source':
                 [dict(id=1, pdt=datetime(2019, 1, 1), value='c', dt=datetime(2017, 5, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, pdt=datetime(2019, 1, 1), value='d', dt=datetime(2017, 6, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2017, 5, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2017, 6, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2017, 5, 1),
                       edt=datetime(2017, 5, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2017, 6, 1),
                       edt=datetime(2017, 6, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2017, 5, 1),
                       evalue='c'),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2017, 6, 1),
                       evalue='d')
                  ],
         }
     ]
     },
    {'type': 'attr_new_partition.json',
     'tests': [
         {
             'source':
                 [dict(id=1, pdt=datetime(2019, 1, 1), value='a', dt=datetime(2019, 1, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, pdt=datetime(2019, 1, 1), value='b', dt=datetime(2019, 3, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       edt=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ]
         },
         {
             'source':
                 [dict(id=1, pdt=datetime(2019, 1, 1), value='aa', dt=datetime(2019, 1, 2),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, pdt=datetime(2019, 1, 1), value='bb', dt=datetime(2019, 3, 2),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       edt=datetime(2019, 3, 2))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a', utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       evalue='aa', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b', utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       evalue='bb', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=1, pdt=datetime(2019, 1, 1), value='aaa', dt=datetime(2018, 1, 2),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, pdt=datetime(2019, 1, 1), value='bbb', dt=datetime(2018, 3, 2),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       edt=datetime(2019, 3, 2))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2),
                       evalue='aaa', utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a', utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       evalue='aa', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2),
                       evalue='bbb', utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b', utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       evalue='bb', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=1, pdt=datetime(2019, 1, 1), value='aaaa', dt=datetime(2018, 4, 2),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, pdt=datetime(2019, 1, 1), value='bbbb', dt=datetime(2018, 6, 2),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       edt=datetime(2019, 3, 2))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2),
                       evalue='aaa', utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2),
                       evalue='aaaa', utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a', utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       evalue='aa', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2),
                       evalue='bbb', utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2),
                       evalue='bbbb', utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b', utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       evalue='bb', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=1, pdt=datetime(2019, 1, 1), value='cccc', dt=datetime(2018, 4, 2),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, pdt=datetime(2019, 1, 1), value='dddd', dt=datetime(2018, 6, 2),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       edt=datetime(2019, 3, 2))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2),
                       evalue='aaa', utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2),
                       evalue='cccc', utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a', utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       evalue='aa', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2),
                       evalue='bbb', utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2),
                       evalue='dddd', utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b', utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       evalue='bb', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=3, pdt=datetime(2019, 1, 1), value='c', dt=datetime(2019, 1, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, pdt=datetime(2019, 1, 1), value='cc', dt=datetime(2019, 3, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       edt=datetime(2019, 3, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1),
                       edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=3)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2),
                       evalue='aaa', utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2),
                       evalue='cccc', utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a', utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       evalue='aa', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2),
                       evalue='bbb', utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2),
                       evalue='dddd', utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b', utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       evalue='bb', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='c', utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='cc', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=3, pdt=datetime(2019, 1, 1), value='d', dt=datetime(2019, 1, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, pdt=datetime(2019, 1, 1), value='ccc', dt=datetime(2019, 2, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       edt=datetime(2019, 3, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1),
                       edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=3)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2),
                       evalue='aaa', utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2),
                       evalue='cccc', utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a', utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       evalue='aa', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2),
                       evalue='bbb', utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2),
                       evalue='dddd', utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b', utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       evalue='bb', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='d', utc_valid_to_dttm=datetime(2019, 1, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 1),
                       evalue='ccc', utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='cc', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=3, pdt=datetime(2019, 1, 1), value='e', dt=datetime(2019, 1, 10),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, pdt=datetime(2019, 1, 1), value='f', dt=datetime(2019, 2, 10),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       edt=datetime(2019, 3, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1),
                       edt=datetime(2019, 3, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=3)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2),
                       evalue='aaa', utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2),
                       evalue='cccc', utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a', utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       evalue='aa', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2),
                       evalue='bbb', utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2),
                       evalue='dddd', utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b', utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       evalue='bb', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='d', utc_valid_to_dttm=datetime(2019, 1, 9, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 10),
                       evalue='e', utc_valid_to_dttm=datetime(2019, 1, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 1),
                       evalue='ccc', utc_valid_to_dttm=datetime(2019, 2, 9, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 10),
                       evalue='f', utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='cc', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         },
         {
             'source':
                 [dict(id=3, pdt=datetime(2019, 1, 1), value='z', dt=datetime(2019, 1, 10),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, pdt=datetime(2019, 1, 1), value='rr', dt=datetime(2019, 2, 5),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, pdt=datetime(2019, 1, 1), value='rr1', dt=datetime(2019, 2, 7),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=3, pdt=datetime(2019, 1, 1), value='rr2', dt=datetime(2019, 4, 1),
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1))
                  ],
             'edt':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       edt=datetime(2019, 1, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       edt=datetime(2019, 3, 2)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 4, 1),
                       edt=datetime(2019, 4, 1))
                  ],
             'eid':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=1),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       eid=2),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1),
                       eid=3)
                  ],
             'evalue':
                 [dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 2),
                       evalue='aaa', utc_valid_to_dttm=datetime(2018, 4, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2018, 4, 2),
                       evalue='cccc', utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='a', utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2),
                       evalue='aa', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 3, 2),
                       evalue='bbb', utc_valid_to_dttm=datetime(2018, 6, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2018, 6, 2),
                       evalue='dddd', utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='b', utc_valid_to_dttm=datetime(2019, 3, 1, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(2), utc_valid_from_dttm=datetime(2019, 3, 2),
                       evalue='bb', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1),
                       evalue='d', utc_valid_to_dttm=datetime(2019, 1, 9, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 10),
                       evalue='z', utc_valid_to_dttm=datetime(2019, 1, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 1),
                       evalue='ccc', utc_valid_to_dttm=datetime(2019, 2, 4, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 5),
                       evalue='rr', utc_valid_to_dttm=datetime(2019, 2, 6, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 7),
                       evalue='rr1', utc_valid_to_dttm=datetime(2019, 2, 9, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 10),
                       evalue='f', utc_valid_to_dttm=datetime(2019, 2, 28, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 3, 1),
                       evalue='cc', utc_valid_to_dttm=datetime(2019, 3, 31, 23, 59, 59)),
                  dict(_source_id=oktell, pdt=datetime(2019, 1, 1), id=get_md5(3), utc_valid_from_dttm=datetime(2019, 4, 1),
                       evalue='rr2', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
                  ],
         }
     ]
     }
]

link_1 = [
    {'type': 'link_deprecated.json',
     'tests': [
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 1), e1=1, e2=2, e3=3,
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, dt=datetime(2019, 2, 1), e1=4, e2=5, e3=6,
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(4), e2=get_md5(5), e3=get_md5(6), utc_valid_from_dttm=datetime(2019, 2, 1), _deleted_flg=False)
                  ]
         },
         {
             'source':
                 [dict(id=4, dt=datetime(2019, 2, 2), e1=1, e2=2, e3=5,
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(4), e2=get_md5(5), e3=get_md5(6), utc_valid_from_dttm=datetime(2019, 2, 1), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(5), utc_valid_from_dttm=datetime(2019, 2, 2), _deleted_flg=False)
                  ]
         }
     ]
     },

    {'type': 'link.json',
     'tests': [
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 1), e1=1, e2=2, e3=3,
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, dt=datetime(2019, 2, 1), e1=4, e2=5, e3=6,
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(9999,12,31,23,59,59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(4), e2=get_md5(5), e3=get_md5(6), utc_valid_from_dttm=datetime(2019, 2, 1), utc_valid_to_dttm=datetime(9999,12,31,23,59,59), _deleted_flg=False)
                  ]
         },
         {
             'source':
                 [dict(id=4, dt=datetime(2019, 2, 2), e1=1, e2=2, e3=5,
                       _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(9999,12,31,23,59,59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(4), e2=get_md5(5), e3=get_md5(6), utc_valid_from_dttm=datetime(2019, 2, 1), utc_valid_to_dttm=datetime(9999,12,31,23,59,59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(5), utc_valid_from_dttm=datetime(2019, 2, 2), utc_valid_to_dttm=datetime(9999,12,31,23,59,59), _deleted_flg=False)
                  ]
         }
     ]
     },

    {'type': 'link_hist.json',
     'tests': [
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 1), e1=1, e2=2, e3=3, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(9999,12,31,23,59,59))
                  ]
         },
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 4), e1=1, e2=2, e3=4, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59)),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(4), utc_valid_from_dttm=datetime(2019, 1, 4), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))

                  ]
         },
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 2), e1=1, e2=2, e3=5, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=1, dt=datetime(2019, 1, 6), e1=1, e2=2, e3=6, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(5), utc_valid_from_dttm=datetime(2019, 1, 2), utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59)),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(4), utc_valid_from_dttm=datetime(2019, 1, 4), utc_valid_to_dttm=datetime(2019, 1, 5, 23, 59, 59)),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(6), utc_valid_from_dttm=datetime(2019, 1, 6), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))

                  ]
         },
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 2), e1=1, e2=2, e3=7, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(7), utc_valid_from_dttm=datetime(2019, 1, 2), utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59)),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(4), utc_valid_from_dttm=datetime(2019, 1, 4), utc_valid_to_dttm=datetime(2019, 1, 5, 23, 59, 59)),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(6), utc_valid_from_dttm=datetime(2019, 1, 6), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))

                  ]
         }
     ]
     }
]

params3 = [
    {'type': 'attr_new2.json',
     'tests': [
         {
             'source':
                 [dict(id=1, value='a', dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  ]
         },
         {
             'source':
                 [dict(id=1, value='a', dt=datetime(2019, 3, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  ]
         },
         {
             'source':
                 [dict(id=2, value='b', dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='aa', dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 15, 30)),
                  dict(id=2, value='cc', dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 17, 30)),
                  dict(id=2, value='d', dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=2, value='b', dt=datetime(2019, 3, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  ],
             'eid':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), eid=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 1, 1), eid=2),
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='b',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),

                  ]
         },
     ]
     }
]


params1 = [
    {'type': 'group1.json',
     'tests': [
         {
             'source':
                 [dict(ent_id=1, attr1=1, attr2='a', attr3=datetime(2020, 1, 1, 00, 30), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  dict(ent_id=2, attr1=66, attr2=None, attr3=datetime(2020, 1, 1, 1, 30), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), ent_id=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), ent_id=2),
                  ],
             'g1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), attr1=1,attr2='a',attr3=datetime(2020, 1, 1, 00, 30),),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), attr1=66,attr2=None,attr3=datetime(2020, 1, 1, 1, 30),),
                  ]
         },
         {
             'source':
                 [dict(ent_id=1, attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 35), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  dict(ent_id=2, attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 35), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), ent_id=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), ent_id=2),
                  ],
             'g1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 35), attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 35), ),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 35), attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 35), ),
                  ]
         },
         {
             'source':
                 [dict(ent_id=1, attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 15), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  dict(ent_id=2, attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 15), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 15)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 15)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), ent_id=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), ent_id=2),
                  ],
             'g1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 35), attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 35), ),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 35), attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 35), ),
                  ]
         },
         {
             'source':
                 [dict(ent_id=1, attr1=None, attr2='qq', attr3=datetime(2020, 1, 1, 00, 10), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  dict(ent_id=2, attr1=None, attr2='qq', attr3=datetime(2020, 1, 1, 1, 10), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 10)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 10)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), ent_id=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), ent_id=2),
                  ],
             'g1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 35), attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 35), ),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 35), attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 35), ),
                  ]
         },
         {
             'source':
                 [dict(ent_id=1, attr1=22, attr2='qq', attr3=datetime(2020, 1, 1, 00, 45), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  dict(ent_id=2, attr1=33, attr2='pp', attr3=datetime(2020, 1, 1, 1, 45), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 10)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 10)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), ent_id=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), ent_id=2),
                  ],
             'g1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 45), attr1=22, attr2='qq', attr3=datetime(2020, 1, 1, 00, 45), ),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 45), attr1=33, attr2='pp', attr3=datetime(2020, 1, 1, 1, 45), ),
                  ]
         },
     ]
     }
]


params1 = [
    {'type': 'group2.json',
     'tests': [
         {
             'source':
                 [dict(ent_id=1, attr1=1, attr2='a', attr3=datetime(2020, 1, 1, 00, 30), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  dict(ent_id=2, attr1=66, attr2=None, attr3=datetime(2020, 1, 1, 1, 30), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), ent_id=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), ent_id=2),
                  ],
             'g1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), attr1=1, attr2='a', attr3=datetime(2020, 1, 1, 00, 30),),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), attr1=66, attr2=None, attr3=datetime(2020, 1, 1, 1, 30),),
                  ]
         },
         {
             'source':
                 [dict(ent_id=1, attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 35), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  dict(ent_id=2, attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 35), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), ent_id=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), ent_id=2),
                  ],
             'g1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), utc_valid_to_dttm=datetime(2020, 1, 1, 00, 35) - timedelta(seconds=1), attr1=1, attr2='a', attr3=datetime(2020, 1, 1, 00, 30),),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), utc_valid_to_dttm=datetime(2020, 1, 1, 1, 35) - timedelta(seconds=1), attr1=66, attr2=None, attr3=datetime(2020, 1, 1, 1, 30),),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 35), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 35), ),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 35), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 35), ),
                  ]
         },
         {
             'source':
                 [dict(ent_id=1, attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 15), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  dict(ent_id=2, attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 15), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 15)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 15)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), ent_id=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), ent_id=2),
                  ],
             'g1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 15), utc_valid_to_dttm=datetime(2020, 1, 1, 00, 30) - timedelta(seconds=1), attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 15),),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 15), utc_valid_to_dttm=datetime(2020, 1, 1, 1, 30) - timedelta(seconds=1), attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 15),),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), utc_valid_to_dttm=datetime(2020, 1, 1, 00, 35) - timedelta(seconds=1), attr1=1, attr2='a', attr3=datetime(2020, 1, 1, 00, 30), ),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), utc_valid_to_dttm=datetime(2020, 1, 1, 1, 35) - timedelta(seconds=1), attr1=66, attr2=None, attr3=datetime(2020, 1, 1, 1, 30), ),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 35), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 35), ),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 35), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 35), ),
                  ]
         },
         {
             'source':
                 [dict(ent_id=1, attr1=None, attr2='qq', attr3=datetime(2020, 1, 1, 00, 10), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  dict(ent_id=2, attr1=None, attr2='qq', attr3=datetime(2020, 1, 1, 1, 10), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 10)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 10)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), ent_id=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), ent_id=2),
                  ],
             'g1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 10), utc_valid_to_dttm=datetime(2020, 1, 1, 00, 15) - timedelta(seconds=1), attr1=None, attr2='qq', attr3=datetime(2020, 1, 1, 00, 10),),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 10), utc_valid_to_dttm=datetime(2020, 1, 1, 1, 15) - timedelta(seconds=1), attr1=None, attr2='qq', attr3=datetime(2020, 1, 1, 1, 10),),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 15), utc_valid_to_dttm=datetime(2020, 1, 1, 00, 30) - timedelta(seconds=1), attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 15),),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 15), utc_valid_to_dttm=datetime(2020, 1, 1, 1, 30) - timedelta(seconds=1), attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 15),),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), utc_valid_to_dttm=datetime(2020, 1, 1, 00, 35) - timedelta(seconds=1), attr1=1, attr2='a', attr3=datetime(2020, 1, 1, 00, 30), ),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), utc_valid_to_dttm=datetime(2020, 1, 1, 1, 35) - timedelta(seconds=1), attr1=66, attr2=None, attr3=datetime(2020, 1, 1, 1, 30), ),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 35), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 35), ),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 35), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 35), ),
                  ]
         },
         {
             'source':
                 [dict(ent_id=1, attr1=22, attr2='qq', attr3=datetime(2020, 1, 1, 00, 45), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  dict(ent_id=2, attr1=33, attr2='pp', attr3=datetime(2020, 1, 1, 1, 45), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 10)),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 10)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), ent_id=1),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), ent_id=2),
                  ],
             'g1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 10), utc_valid_to_dttm=datetime(2020, 1, 1, 00, 15) - timedelta(seconds=1), attr1=None, attr2='qq', attr3=datetime(2020, 1, 1, 00, 10),),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 10), utc_valid_to_dttm=datetime(2020, 1, 1, 1, 15) - timedelta(seconds=1), attr1=None, attr2='qq', attr3=datetime(2020, 1, 1, 1, 10),),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 15), utc_valid_to_dttm=datetime(2020, 1, 1, 00, 30) - timedelta(seconds=1), attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 15),),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 15), utc_valid_to_dttm=datetime(2020, 1, 1, 1, 30) - timedelta(seconds=1), attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 15),),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 30), utc_valid_to_dttm=datetime(2020, 1, 1, 00, 35) - timedelta(seconds=1), attr1=1, attr2='a', attr3=datetime(2020, 1, 1, 00, 30), ),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 30), utc_valid_to_dttm=datetime(2020, 1, 1, 1, 35) - timedelta(seconds=1), attr1=66, attr2=None, attr3=datetime(2020, 1, 1, 1, 30), ),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 35), utc_valid_to_dttm=datetime(2020, 1, 1, 00, 45) - timedelta(seconds=1), attr1=None, attr2='a', attr3=datetime(2020, 1, 1, 00, 35), ),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 35), utc_valid_to_dttm=datetime(2020, 1, 1, 1, 45) - timedelta(seconds=1), attr1=None, attr2='zz', attr3=datetime(2020, 1, 1, 1, 35), ),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 00, 45), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), attr1=22, attr2='qq', attr3=datetime(2020, 1, 1, 00, 45), ),
                  dict(_source_id=oktell, id=get_md5(2), utc_valid_from_dttm=datetime(2020, 1, 1, 1, 45), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), attr1=33, attr2='qq', attr3=datetime(2020, 1, 1, 1, 45), ),
                  ]
         },
     ]
     }
]


check_delete_attribute = [
    {'type': 'check_delete_attribute.json',
     'tests': [
         {
             'source':
                 [dict(ent_id=1, attr1='a', attr2='a', bdt=datetime(2020, 1, 1, 0, 30), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), ent_id=1),
                  ],
             'attr1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), attr1='a'),
                  ],
             'attr2':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), attr2='a', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  ],
         },
         {
             'source':
                 [dict(ent_id=1, attr1='a', attr2='a', bdt=datetime(2020, 1, 1, 00, 15), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 15)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), ent_id=1),
                  ],
             'attr1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), attr1='a'),
                  ],
             'attr2':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 15), attr2='a', utc_valid_to_dttm=datetime(2020, 1, 1, 0, 29, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), attr2='a', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),

                  ],
         },
         {
             'source':
                 [dict(ent_id=1, attr1=None, attr2=None, bdt=datetime(2020, 1, 1, 00, 45), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 15)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), ent_id=1),
                  ],
             'attr1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 45), attr1=None),
                  ],
             'attr2':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 15), attr2='a', utc_valid_to_dttm=datetime(2020, 1, 1, 0, 29, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), attr2='a', utc_valid_to_dttm=datetime(2020, 1, 1, 0, 44, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 45), attr2=None, utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),

                  ],
         },
     ]
     }
]


check_microsecond = [
    {'type': 'check_microsecond.json',
     'tests': [
         {
             'source':
                 [dict(ent_id=1, attr1='a', attr2='a', bdt=datetime(2020, 1, 1, 0, 30, 0, 300), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  dict(ent_id=1, attr1='z', attr2='z', bdt=datetime(2020, 1, 1, 0, 30, 0, 100), _etl_processed_dttm=datetime(2020, 1, 1, 21, 31)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), ent_id=1),
                  ],
             'attr1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), attr1='z'),
                  ],
             'attr2':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), attr2='z', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  ],
         },
     ]
     }
]


check_microsecond_same_etl_dttm = [
    {'type': 'check_microsecond_same_etl_dttm.json',
     'tests': [
         {
             'source':
                 [dict(ent_id=1, attr1='a', attr2='a', bdt=datetime(2020, 1, 1, 0, 30, 0, 300), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  dict(ent_id=1, attr1='z', attr2='z', bdt=datetime(2020, 1, 1, 0, 30, 0, 100), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), ent_id=1),
                  ],
             'attr1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), attr1='a'),
                  ],
             'attr2':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), attr2='a', utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  ],
         },
     ]
     }
]


# провяреям:
# если для IGNORE пришло две записи в разных ETL, то взять нужно первую.
# если для UPDATE пришло две записи в разных ETL, то взять нужно последнюю
check_ignore_with_two_etldt = [
    {'type': 'check_ignore_with_two_etldt.json',
     'tests': [
         {
             'source':
                 [dict(ent_id=1, attr1='a', attr2='a', bdt=datetime(2020, 1, 1, 0, 30, 0), _etl_processed_dttm=datetime(2020, 1, 1, 21, 30)),
                  dict(ent_id=1, attr1='z', attr2='z', bdt=datetime(2020, 1, 1, 0, 30, 0), _etl_processed_dttm=datetime(2020, 1, 1, 21, 31)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30)),
                  ],
             'ent_id':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), ent_id=1),
                  ],
             'attr1':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), attr1='a'),
                  ],
             'attr2':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2020, 1, 1, 0, 30), attr2='z'),
                  ],
         },
     ]
     }
]


link_deleted = [
    {'type': 'link_deleted_deprecated.json',
     'tests': [
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 1), e1=1, e2=2, e3=3, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=None)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), _deleted_flg=False)
                  ]
         },
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 2, 2), e1=1, e2=2, e3=3, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=True)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 2), _deleted_flg=True)
                  ]
         },
         {
             'source':
                 [dict(id=2, dt=datetime(2019, 4, 2), e1=5, e2=5, e3=5, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=False)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 2), _deleted_flg=True),
                  dict(_source_id=oktell, e1=get_md5(5), e2=get_md5(5), e3=get_md5(5), utc_valid_from_dttm=datetime(2019, 4, 2), _deleted_flg=False),

                  ]
         },
         {
             'source':
                 [dict(id=2, dt=datetime(2019, 4, 1), e1=5, e2=5, e3=5, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=True)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 2), _deleted_flg=True),
                  dict(_source_id=oktell, e1=get_md5(5), e2=get_md5(5), e3=get_md5(5), utc_valid_from_dttm=datetime(2019, 4, 2), _deleted_flg=False),

                  ]
         },
         {
             'source':
                 [dict(id=2, dt=datetime(2019, 4, 3), e1=5, e2=5, e3=5, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=True)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 2), _deleted_flg=True),
                  dict(_source_id=oktell, e1=get_md5(5), e2=get_md5(5), e3=get_md5(5), utc_valid_from_dttm=datetime(2019, 4, 3), _deleted_flg=True),

                  ]
         },
     ]
     },
    {'type': 'link_deleted.json',
     'tests': [
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 1), e1=1, e2=2, e3=3, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=None)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(9999,12,31,23,59,59), _deleted_flg=False)
                  ]
         },
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 2, 2), e1=1, e2=2, e3=3, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=True)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 2, 1, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 2), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=True)

                  ]
         },
         {
             'source':
                 [dict(id=2, dt=datetime(2019, 4, 2), e1=5, e2=5, e3=5, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=False)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 2, 1, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 2), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=True),
                  dict(_source_id=oktell, e1=get_md5(5), e2=get_md5(5), e3=get_md5(5), utc_valid_from_dttm=datetime(2019, 4, 2), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=False),

                  ]
         },
         {
             'source':
                 [dict(id=2, dt=datetime(2019, 4, 1), e1=5, e2=5, e3=5, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=True)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 2, 1, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 2), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=True),
                  dict(_source_id=oktell, e1=get_md5(5), e2=get_md5(5), e3=get_md5(5), utc_valid_from_dttm=datetime(2019, 4, 1), utc_valid_to_dttm=datetime(2019, 4, 1, 23, 59, 59), _deleted_flg=True),
                  dict(_source_id=oktell, e1=get_md5(5), e2=get_md5(5), e3=get_md5(5), utc_valid_from_dttm=datetime(2019, 4, 2), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=False),

                  ]
         },
         {
             'source':
                 [dict(id=2, dt=datetime(2019, 4, 3), e1=5, e2=5, e3=5, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=True)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 2, 1, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 2), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=True),
                  dict(_source_id=oktell, e1=get_md5(5), e2=get_md5(5), e3=get_md5(5), utc_valid_from_dttm=datetime(2019, 4, 1), utc_valid_to_dttm=datetime(2019, 4, 1, 23, 59, 59), _deleted_flg=True),
                  dict(_source_id=oktell, e1=get_md5(5), e2=get_md5(5), e3=get_md5(5), utc_valid_from_dttm=datetime(2019, 4, 2), utc_valid_to_dttm=datetime(2019, 4, 2, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(5), e2=get_md5(5), e3=get_md5(5), utc_valid_from_dttm=datetime(2019, 4, 3), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=True),
                  ]
         },
     ]
     },
    {'type': 'link_deleted_hist.json',
     'tests': [
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 1), e1=1, e2=2, e3=3, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=False)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(9999,12,31,23,59,59), _deleted_flg=False)
                  ]
         },
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 4), e1=1, e2=2, e3=4, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=True)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(4), utc_valid_from_dttm=datetime(2019, 1, 4), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=True)

                  ]
         },
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 2), e1=1, e2=2, e3=5, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=True),
                  dict(id=1, dt=datetime(2019, 1, 6), e1=1, e2=2, e3=6, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=False)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(5), utc_valid_from_dttm=datetime(2019, 1, 2), utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59), _deleted_flg=True),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(4), utc_valid_from_dttm=datetime(2019, 1, 4), utc_valid_to_dttm=datetime(2019, 1, 5, 23, 59, 59), _deleted_flg=True),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(6), utc_valid_from_dttm=datetime(2019, 1, 6), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=False)

                  ]
         },
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 2), e1=1, e2=2, e3=7, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=False)
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(7), utc_valid_from_dttm=datetime(2019, 1, 2), utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(4), utc_valid_from_dttm=datetime(2019, 1, 4), utc_valid_to_dttm=datetime(2019, 1, 5, 23, 59, 59), _deleted_flg=True),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(6), utc_valid_from_dttm=datetime(2019, 1, 6), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=False)

                  ]
         }
     ]
     }
]


link_hist_partition = [
    {'type': 'link_hist_partition.json',
     'tests': [
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 1), pdt=datetime(2019, 1, 1), e1=1, e2=2, e3=3, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), zzz=datetime(2019, 1, 1), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(9999,12,31,23,59,59), _deleted_flg=False)
                  ]
         },
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 4), pdt=datetime(2019, 1, 1), e1=1, e2=2, e3=4, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), zzz=datetime(2019, 1, 1), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(4), zzz=datetime(2019, 1, 1), utc_valid_from_dttm=datetime(2019, 1, 4), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=False)

                  ]
         },
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 2), pdt=datetime(2019, 1, 1), e1=1, e2=2, e3=5, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=1, dt=datetime(2019, 1, 6), pdt=datetime(2019, 1, 1), e1=1, e2=2, e3=6, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), zzz=datetime(2019, 1, 1), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(5), zzz=datetime(2019, 1, 1), utc_valid_from_dttm=datetime(2019, 1, 2), utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(4), zzz=datetime(2019, 1, 1), utc_valid_from_dttm=datetime(2019, 1, 4), utc_valid_to_dttm=datetime(2019, 1, 5, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(6), zzz=datetime(2019, 1, 1), utc_valid_from_dttm=datetime(2019, 1, 6), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=False)

                  ]
         },
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 2), pdt=datetime(2019, 1, 1), e1=1, e2=2, e3=7, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30))
                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), zzz=datetime(2019, 1, 1), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(7), zzz=datetime(2019, 1, 1), utc_valid_from_dttm=datetime(2019, 1, 2), utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(4), zzz=datetime(2019, 1, 1), utc_valid_from_dttm=datetime(2019, 1, 4), utc_valid_to_dttm=datetime(2019, 1, 5, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(6), zzz=datetime(2019, 1, 1), utc_valid_from_dttm=datetime(2019, 1, 6), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=False)

                  ]
         }
     ]
     }
]


attr_new_null = [
    {'type': 'attr_new_null.json',
     'tests': [
         {
             'source':
                 [dict(id=1, value='a', dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  ]
         },
         {
             'source':
                 [dict(id=1, value=None, dt=datetime(2019, 1, 2), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1)),
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue=None,
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),

                  ]
         },
         {
             'source':
                 [dict(id=1, value=None, dt=datetime(2018, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1)),
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1), evalue=None,
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue=None,
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  ]
         },
         {
             'source':
                 [dict(id=1, value=None, dt=datetime(2018, 1, 3), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=1, value='b', dt=datetime(2019, 1, 3), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=1, value=None, dt=datetime(2019, 1, 4), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=1, value=None, dt=datetime(2019, 1, 5), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=1, value='c', dt=datetime(2019, 1, 6), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=1, value='c', dt=datetime(2019, 1, 7), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1)),
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1), evalue=None,
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue=None,
                       utc_valid_to_dttm=datetime(2019, 1, 2, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 3), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 4), evalue=None,
                       utc_valid_to_dttm=datetime(2019, 1, 5, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 6), evalue='c',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  ]
         },
         {
             'source':
                 [dict(id=1, value='c', dt=datetime(2019, 1, 5), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1)),
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1), evalue=None,
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue='a',
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue=None,
                       utc_valid_to_dttm=datetime(2019, 1, 2, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 3), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 4), evalue=None,
                       utc_valid_to_dttm=datetime(2019, 1, 4, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 5), evalue='c',
                       utc_valid_to_dttm=datetime(2019, 1, 5, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 6), evalue='c',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  ]
         },
         {
             'source':
                 [dict(id=1, value=None, dt=datetime(2019, 1, 1), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1)),
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1), evalue=None,
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue=None,
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue=None,
                       utc_valid_to_dttm=datetime(2019, 1, 2, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 3), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 4), evalue=None,
                       utc_valid_to_dttm=datetime(2019, 1, 4, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 5), evalue='c',
                       utc_valid_to_dttm=datetime(2019, 1, 5, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 6), evalue='c',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  ]
         },
         {
             'source':
                 [dict(id=1, value='b', dt=datetime(2019, 1, 7), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=1, value='c', dt=datetime(2019, 1, 8), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1)),
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1), evalue=None,
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue=None,
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue=None,
                       utc_valid_to_dttm=datetime(2019, 1, 2, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 3), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 4), evalue=None,
                       utc_valid_to_dttm=datetime(2019, 1, 4, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 5), evalue='c',
                       utc_valid_to_dttm=datetime(2019, 1, 5, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 6), evalue='c',
                       utc_valid_to_dttm=datetime(2019, 1, 6, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 7), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 1, 7, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 8), evalue='c',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  ]
         },
         {
             'source':
                 [dict(id=1, value='d', dt=datetime(2019, 1, 8), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  dict(id=1, value='c', dt=datetime(2019, 1, 9), _etl_processed_dttm=datetime(2019, 1, 3, 18, 30)),
                  ],
             'hub':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1)),
                  ],
             'evalue':
                 [dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2018, 1, 1), evalue=None,
                       utc_valid_to_dttm=datetime(2018, 12, 31, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 1), evalue=None,
                       utc_valid_to_dttm=datetime(2019, 1, 1, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 2), evalue=None,
                       utc_valid_to_dttm=datetime(2019, 1, 2, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 3), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 1, 3, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 4), evalue=None,
                       utc_valid_to_dttm=datetime(2019, 1, 4, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 5), evalue='c',
                       utc_valid_to_dttm=datetime(2019, 1, 5, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 6), evalue='c',
                       utc_valid_to_dttm=datetime(2019, 1, 6, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 7), evalue='b',
                       utc_valid_to_dttm=datetime(2019, 1, 7, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 8), evalue='d',
                       utc_valid_to_dttm=datetime(2019, 1, 8, 23, 59, 59)),
                  dict(_source_id=oktell, id=get_md5(1), utc_valid_from_dttm=datetime(2019, 1, 9), evalue='c',
                       utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
                  ]
         },
     ]
     },
]


def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()


if __name__ == '__main__':
    for ent in attr_new_null:
        print(ent['type'])
        print(json.dumps(ent['tests'], default=myconverter))
