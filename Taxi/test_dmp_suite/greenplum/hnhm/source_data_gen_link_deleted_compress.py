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
    {'type': 'link_deleted_compress.json',
     'tests': [
         {
             'source':
                 [dict(id=1, dt=datetime(2019, 1, 1), e1=1, e2=2, e3=3, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=None),
                  dict(id=1, dt=datetime(2019, 2, 2), e1=1, e2=2, e3=3, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=True),
                  dict(id=2, dt=datetime(2019, 4, 2), e1=1, e2=2, e3=3, _etl_processed_dttm=datetime(2019, 1, 3, 18, 30), deleted_flg=False)

                  ],
             'hub':
                 [dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 1, 1), utc_valid_to_dttm=datetime(2019, 2, 1, 23, 59, 59), _deleted_flg=False),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 2, 2), utc_valid_to_dttm=datetime(2019, 4, 1, 23, 59, 59), _deleted_flg=True),
                  dict(_source_id=oktell, e1=get_md5(1), e2=get_md5(2), e3=get_md5(3), utc_valid_from_dttm=datetime(2019, 4, 2), utc_valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59), _deleted_flg=False)

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
