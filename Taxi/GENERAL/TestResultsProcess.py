
# coding: utf-8

import yt.wrapper as yt
import json
from yql.api.v1.client import YqlClient
import os
import base64
from startrek_client import Startrek
import time

### Получаем результаты тестирования у тех людей, кто сейчас в блоке и в реабилитации
def get_test_results(client, action_history_table, rehabilitation_table, online_sessions_table, test_results_tmp_table):
    q = '''
    
use hahn;

$blocked_drivers = (
select 
    *
from 
    range(`{action_history_table}`, `2020-01-01`)
where 
    action not ilike '%message%'
    and action not ilike '%low_tariff%'
);

$with_rehabilitation_flat = (
select 
    unique_driver_id,
    country,
    Yson::ConvertToString(rehabilitation.tariff) as tariff,
    Yson::ConvertToString(rehabilitation.start_dt) as start_dt,
    Yson::ConvertToString(rehabilitation.city) as city,
    Yson::ConvertToString(rehabilitation.locale) as locale
from (select unique_driver_id, country, Yson::ConvertToList(rehabilitations) as rehabilitations from
    `{rehabilitation_table}`)
flatten by 
    rehabilitations as rehabilitation
);


$with_blocked_driver_license = (
select 
    a.unique_driver_id as unique_driver_id,
    a.country as country,
    a.tariff as tariff,
    a.start_dt as start_dt,
    a.city as city,
    a.locale as locale,
    min(b.action_date) as block_date,
    min_by(driver_license, b.action_date) as driver_license,
    min_by(driver_phone, b.action_date) as driver_phone
from 
    $with_rehabilitation_flat as a
join 
    $blocked_drivers as b 
on 
    a.unique_driver_id = b.unique_driver_id
    and a.country = b.country
    and a.tariff = b.tariff
where 
    b.action_date <= a.start_dt
group by 
    a.unique_driver_id as unique_driver_id,
    a.country as country,
    a.tariff as tariff,
    a.start_dt as start_dt,
    a.city as city,
    a.locale as locale
);

$sessions = (
select 
    Yson::ConvertToString(doc.created_at) as test_time,
    Yson::ConvertToInt64(doc.id) as id,
    Yson::ConvertToInt64(doc.grade) as grade,
    Yson::ConvertToString(doc.license) as driver_license,
    Yson::ConvertToString(doc.program) as program
from 
    `{online_sessions_table}`
where 
    Yson::ConvertToString(doc.created_at) >= '2019-07-15'
    -- and Yson::ConvertToInt64(doc.id) in (209, 208, 211, 210)
);

insert into 
    `{test_results_tmp_table}`
with truncate

select 
    a.unique_driver_id as unique_driver_id,
    a.country as country,
    a.tariff as tariff,
    a.start_dt as start_dt,
    a.city as city,
    a.locale as locale,
    a.block_date as block_date,
    a.driver_license as driver_license,
    a.driver_phone as driver_phone,
    min_by(b.id, test_time) as test_id,
    min_by(b.grade, test_time) as grade,
    min_by(b.program, test_time) as program
from 
    $with_blocked_driver_license as a
join 
    $sessions as b
on 
    a.driver_license = b.driver_license
where 
    b.test_time > a.block_date
    and b.program = 'Переаттестация водителей'
group by 
    a.unique_driver_id as unique_driver_id,
    a.country as country,
    a.tariff as tariff,
    a.start_dt as start_dt,
    a.city as city,
    a.locale as locale,
    a.block_date as block_date,
    a.driver_license as driver_license,
    a.driver_phone as driver_phone
    
    '''.format(action_history_table=action_history_table, rehabilitation_table=rehabilitation_table,
               online_sessions_table=online_sessions_table,  test_results_tmp_table=test_results_tmp_table)

    request = client.query(q, syntax_version=1)
    request.run()
    print(request)

### Получаем действия по результатам тестирования и тексты для коммуникации
def send_drivers_to_ticket(token, client, driver_info_table, test_results_tmp_table, executor_profile_table, test_results_history_table):

    url = 'https://st-api.yandex-team.ru'
    st_client = Startrek(useragent='python client', base_url=url, token=token)
    issue = st_client.issues['TAXIQUALITY-1630']
    files_to_ticket = []

    q = '''

use hahn;
pragma yt.InferSchema;

$test_results_clean = (
    select
        *
    from
        `{test_results_tmp_table}` as a
    left only join
        `{test_results_history_table}` as b
        on a.driver_license = b.driver_license
        and a.block_date = b.block_date
);

insert into
    `{driver_info_table}`
with truncate

select distinct
    a.driver_license as driver_license,
    a.driver_phone as driver_phone,
    a.grade as grade,
    b.executor_profile_id as `uuid`
from
    $test_results_clean as a
join
    `{executor_profile_table}` as b
    on a.driver_license = b.driver_license_raw_id
;

commit;

insert into
    `{test_results_history_table}`
select
    *
from
    $test_results_clean

'''.format(driver_info_table=driver_info_table, test_results_tmp_table=test_results_tmp_table,
           executor_profile_table=executor_profile_table, test_results_history_table=test_results_history_table)

    request = client.query(q, syntax_version=1)
    request.run()
    print(request)

    results = hahn.load_result(full_path=driver_info_table)

    # отправляем мониторинг в чатик
    bot = Bot('562014280:AAGvXjD5iU7gV81Sgt3bin-1OUdp3APArnw')

    if len(results) > 0:

        blocks = results[results['grade'] == 2]
        if len(blocks):
            push_block = blocks[['driver_license', 'driver_phone', 'uuid']]
            fname_push_block = 'push_block.csv'
            change_coding(push_block).to_csv(fname_push_block, index=False, sep=';', encoding='utf8')
            files_to_ticket.append(fname_push_block)

            blocks_to_ticket = blocks[['driver_license', 'driver_phone']].drop_duplicates()
            fname_test_block = 'test_block.xlsx'
            change_coding(blocks_to_ticket).to_excel(fname_test_block, index=False)
            files_to_ticket.append(fname_test_block)

            text = '<b>Блокировки за тест: </b>'
            text += str(len(blocks_to_ticket))
            bot.send_message(chat=chat_id, html_parse='html', message=text)
            bot.send_dataframe(blocks_to_ticket, chat=chat_id, filename=fname_test_block)

        unblocks = results[results['grade'] == 4]
        if len(unblocks):
            push_unblock = unblocks[['driver_license', 'driver_phone', 'uuid']]
            fname_push_unblock = 'push_unblock.csv'
            change_coding(push_unblock).to_csv(fname_push_unblock, index=False, sep=';', encoding='utf8')
            files_to_ticket.append(fname_push_unblock)

            unblocks_to_ticket = unblocks[['driver_license', 'driver_phone']].drop_duplicates()
            fname_test_unblock = 'test_unblock.xlsx'
            change_coding(unblocks_to_ticket).to_excel(fname_test_unblock, index=False)
            files_to_ticket.append(fname_test_unblock)

            text = '<b>Разблокировки за тест: </b>'
            text += str(len(unblocks_to_ticket))
            bot.send_message(chat=chat_id, html_parse='html', message=text)
            bot.send_dataframe(unblocks_to_ticket, chat=chat_id, filename=fname_test_unblock)

        text = ("""Данное сообщение сгенерировано автоматически.
                \nТут водители на блокировку и разблокировку по результатам тестирования""")

        time.sleep(60)

        for i in range(5):
            try:
                issue.comments.create(text=text,
                                      attachments=files_to_ticket,
                                      summonees=[u'kvdavydova', u'fromvolga', u'lavr-tsiporin', u'smolyanov-i-v'])
                break
            except Exception:
                continue


    q = '''

use hahn;

$blocks = (
select distinct a.driver_license_pd_id as driver_license_pd_id
from (select * from range(`home/taxi-dwh/ods/blocklist/event_log`, `2021-01-01`)
where action_type = 'add') as a
left only join (select * from range(`home/taxi-dwh/ods/blocklist/event_log`, `2021-01-01`)
where action_type = 'remove') as b
on a.`block_id` = b.`block_id`
);

$blocks_hist = (
select * from range(`home/taxi-dwh/ods/blocklist/event_log`, `2021-01-01`)
where driver_license_pd_id is not null
);

$rating_blocks =
select a.*, b.driver_license_pd_id as driver_license_pd_id from
    (select distinct driver_license, `grade` from `home/taxi-analytics/kvdavydova/new_rating/driver_info`) as a
left join (select distinct `driver_license_raw_id`, driver_license_pd_id
    from  `//home/taxi-dwh/ods/dbdrivers/executor_profile/executor_profile`) as b
on a.driver_license = b.driver_license_raw_id;

insert into `home/taxi-analytics/kvdavydova/new_rating/driver_info_with_blocks`
with truncate
select
    a.driver_license as driver_license,
    a.`grade` as grade,
    a.driver_license_pd_id as driver_license_pd_id,
    h.`utc_event_dttm` as `utc_event_dttm`,
    h.`action_type` as `action_type`,
    h.`taximeter_park_id` as `taximeter_park_id`,
    h.`reason_code` as `reason_code`,
    h.`block_comment` as `block_comment`
from
    $rating_blocks as a
join
    $blocks as b
on
    a.driver_license_pd_id = b.driver_license_pd_id
left join
    $blocks_hist as h
on
    a.driver_license_pd_id = h.driver_license_pd_id

    '''
    request = client.query(q, syntax_version=1)
    request.run()
    print(request)
    if not request.get_results().is_success:
        bot.send_message(chat=creator, message='Скрипт по получению блокировок для водителей на разблок упал \n'
                                               + str(request))
        raise Exception('Скрипт по получению блокировок для водителей на разблок упал \n' + str(request))

    results = hahn.load_result(full_path='//home/taxi-analytics/kvdavydova/new_rating/driver_info_with_blocks')
    if len(results) > 0:
        print('driver_info_with_blocks')
        fname_test_block = 'driver_info_with_blocks.xlsx'
        change_coding(results).to_excel(fname_test_block, index=False)

        text = '<b>Водители с результатами теста и историей блоков </b>'
        bot.send_message(chat=chat_id, html_parse='html', message=text)
        bot.send_dataframe(results, chat=chat_id, filename=fname_test_block)



if __name__ == '__main__':

    creator = 68010842
    chat_id = -1001349744028

    try:

        import numpy as np
        import pandas as pd
        from business_models import hahn, change_coding
        from business_models.botolib import Bot

        yql_config = json.load(open(os.path.expanduser("~") + "/mylib_config.json"))
        token = yql_config['quality_robot_token']
        client = YqlClient(token=token)

        yt.config.set_proxy('hahn')
        yql_config = json.load(open(os.path.expanduser("~") + "/mylib_config.json"))
        token = yql_config['quality_robot_token']
        yt.config['token'] = token

        st_token = yql_config['st_token']

        #используемые таблички
        rehabilitation_table = '//home/taxi-analytics/kvdavydova/new_rating/rehabilitation'
        action_history_table = '//home/taxi-analytics/kvdavydova/new_rating/action_history'
        online_sessions_table = '//home/taxi-dwh/raw/education/online_sessions/online_sessions'
        test_results_tmp_table = '//home/taxi-analytics/kvdavydova/new_rating/test_results_tmp'
        executor_profile_table = '//home/taxi-dwh/ods/dbdrivers/executor_profile/executor_profile'
        driver_info_table = '//home/taxi-analytics/kvdavydova/new_rating/driver_info'
        test_results_history_table = '//home/taxi-analytics/kvdavydova/new_rating/test_results_history'

        print('get_test_results')
        get_test_results(client, action_history_table, rehabilitation_table, online_sessions_table, test_results_tmp_table)
        print('send_drivers_to_ticket')
        send_drivers_to_ticket(st_token, client, driver_info_table, test_results_tmp_table, executor_profile_table, test_results_history_table)

    except KeyboardInterrupt:
        exit()
    except Exception as e:
        bot = Bot('562014280:AAGvXjD5iU7gV81Sgt3bin-1OUdp3APArnw')
        bot.send_message(creator, 'TestResultsProcess  ' + str(e))
        print(e)
        exit()
