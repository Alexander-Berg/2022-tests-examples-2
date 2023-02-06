import datetime

NOW_TZ = datetime.timezone.utc
NOW_DT = datetime.datetime(2021, 3, 13, 7, 19, 00, tzinfo=NOW_TZ)
NOW = NOW_DT.isoformat()

JOB_ID = 'job_id'
YANDEX_UID = 'yandex_uid'
ENTITY_TYPE = 'orders'
ENTITY_ID_NAME = 'item_id'
ANONYM_ID = 'anonym_id'
