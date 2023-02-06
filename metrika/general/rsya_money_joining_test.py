# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import itertools
from functools import reduce

from metr_utils.databases import clickhouse as ch, yql_db
import yt.wrapper as yt
from metr_utils import generate_query


yt.config.set_proxy('hahn.yt.yandex.net')


def strdtuple(input_list):
    return str(tuple(["%d" % c for c in input_list])).replace("'", "")


def strtuple(input_list):
    return str(tuple(['"%d"' % c for c in input_list])).replace("'", '')


def all_subsequences(iterable):
    a = tuple(iterable)
    return reduce(tuple.__add__, (tuple(itertools.combinations(a, _)) for _ in range(len(a) + 1)))


def add_subtotals(df, in_vars, out_vars):
    all_subs = all_subsequences(in_vars)
    return pd.concat([df.assign(**{x: 'Total' for x in comb}).groupby(in_vars + out_vars).sum() for comb in all_subs]).reset_index()


get_dsp_and_watch_log_query = '''
PRAGMA AnsiInForEmptyOrNullableItemsCollections;

--Author : z-sergey
--Parent script : https://bb.yandex-team.ru/projects/METRIKA/repos/metrika-analytics/browse/reports/metrika/rsya_money_joining.py

$getadsid_func =
@@
import simplejson as json
def foo(json_1):
    try: answer = json.loads(json_1).get("__ym",{{}}).get("adSessionID","") if json_1 else ""
    except: answer = ""
    return str(answer)
@@;

$getadsid = Python::foo(Callable<(String?)->String?>, $getadsid_func);

insert into @tmp_dmp
SELECT
    page_id, adsessionid,
    min(cast(eventtime - eventtime % 3600 + 3600*3 as DateTime)) as hour,
    cast(some(UserAgent::Parse(useragent).isMobile) as string) ?? "None" as ismobile,
    some(UserAgent::Parse(useragent).OSFamily)                 ?? "None" as osfamily,
    some(UserAgent::Parse(useragent).OSName)                   ?? "None" as osname,
    some(UserAgent::Parse(useragent).OSVersion)                ?? "None" as osversion,
    sum(cast(partnerprice as double) / 1000000) as partnerprice
from `//statbox/cooked_logs/bs-dsp-cooked-log/v1/1d/{date}`
where page_id is not null
    and page_id in {page_ids}
    and dspfraudbits = 0
    and win = 1 and countertype = 1
    and adsessionid != 0
    and adsessionid is not null
    and Digest::MurMurHash( CAST(Unwrap(cast(uniqid as uint64)) AS String)) % 100u < {my_sample}
group by pageid as page_id, adsessionid
order by adsessionid;

insert into @tmp_watch
select adsessionid
from range(`//logs/bs-watch-log/1d`, `{date_before}`, `{date}`)
where counterid is not null
    and counterid in {str_counter_ids}
    and (params ?? "") like "%__ym%adSessionID%"
group by cast($getadsid(params) as Uint64) as adsessionid
having adsessionid != 0
order by adsessionid;

COMMIT;

select a.*, b.adsessionid is not null as in_watch
from
@tmp_dmp as a
left join
@tmp_watch as b
using(adsessionid)
'''

get_page_counters_query = '''
SELECT *
FROM dictionaries.rsya_report_page_counters{testing_underline}
FORMAT TabSeparatedWithNames
'''

ch_hits_query = '''
SELECT DISTINCT if((InternalParams.Key1[1]) = 'adSessionID', toUInt64OrZero(InternalParams.Key2[1]), 0) AS adsessionid, 1 as in_hits
FROM {hits_table}
WHERE (EventDate = toDate('{date}') or EventDate = toDate('{date_before}'))
    AND (CounterID in {counter_ids})
    AND (adsessionid != 0)
FORMAT TabSeparatedWithNames
'''

ch_visits_query = '''
SELECT adsessionid, page_id, sumIf(Sign * partnerprice/1000000,IsShow=1) as metr_partnerprice
FROM {visits_table}
array join
    YAN.IsShow as IsShow,
    YAN.AdSessionID as adsessionid,
    YAN.PartnerPrice as partnerprice,
    YAN.PageID as page_id
WHERE (StartDate = toDate('{date}') or StartDate = toDate('{date_before}'))
  AND CounterID in {counter_ids}
  AND page_id in {page_ids}
Group by adsessionid, page_id
FORMAT TabSeparatedWithNames
'''


def dump_table(name, table_df):

    data_to_load = table_df[['page_id', 'domain', 'page', 'adsessionid', 'hour', 'in_watch', 'in_hits', 'in_visits', 'metr_partnerprice', 'partnerprice']].T.to_dict().values()

    try:
        yt.remove('//home/metrica-analytics/.tmp/logs/rsya_money_join_bad_adsids/{name}_testing'.format(name=name))
    except:
        pass
    yt.create(
        "table",
        '//home/metrica-analytics/.tmp/logs/rsya_money_join_bad_adsids/{name}_testing'.format(name=name),
        attributes={
            "schema": [
                {"name": "page_id", "type": "uint32"},
                {"name": "domain", "type": "string"},
                {"name": "page", "type": "string"},
                {"name": "adsessionid", "type": "uint64"},
                {"name": "hour", "type": "uint64"},
                {"name": "in_watch", "type": "int64"},
                {"name": "in_hits", "type": "boolean"},
                {"name": "in_visits", "type": "boolean"},
                {"name": "metr_partnerprice", "type": "double"},
                {"name": "partnerprice", "type": "double"},
            ]
        },
    )

    yt.write_table('//home/metrica-analytics/.tmp/logs/rsya_money_join_bad_adsids/{name}_testing'.format(name=name), data_to_load)


def get_data(opts):
    date_yesterday = generate_query.day(opts.date_start, opts.shift - 1)[0]

    str_params = {'testing_underline': '_testing', 'my_sample': 10, 'isbeta': '-beta', 'visits_table': 'visits_test_all', 'hits_table': 'hits_test_all'}

    page_counters = ch.get_df(get_page_counters_query.format(**str_params))

    str_params.update(
        {
            'date': opts.date_start,
            'date_before': date_yesterday,
            'page_ids': strdtuple(page_counters.page_id),
            'str_counter_ids': strtuple(page_counters.counter_id),
            'counter_ids': strdtuple(page_counters.counter_id),
        }
    )

    dsp_adsessions = yql_db.get_df(get_dsp_and_watch_log_query.format(**str_params))

    dsp_adsessions['osversion'] = dsp_adsessions['osversion'].str.split(".").map(lambda x: x[0])
    dsp_adsessions['hour'] = dsp_adsessions.hour.apply(lambda x: int(x.timestamp()))

    hits_adsessions = ch.get_df(ch_hits_query.format(**str_params))

    visits_adsessions = ch.get_df(ch_visits_query.format(**str_params))

    total_df = dsp_adsessions.merge(hits_adsessions, on=["adsessionid"], how='left')
    total_df['in_hits'] = total_df['in_hits'].map(lambda x: not np.isnan(x))

    total_df = total_df.merge(visits_adsessions, on=["adsessionid", "page_id"], how='left')

    total_df['in_visits'] = total_df['metr_partnerprice'].map(lambda x: not np.isnan(x))
    total_df['metr_partnerprice'].fillna(0, inplace=True)
    total_df['metr_partnerprice'] = total_df['metr_partnerprice'].astype('float')
    total_df['adsid_count_dsp'] = 1

    total_df['adsid_count_watch'] = total_df['adsid_count_dsp'] * total_df['in_watch']
    total_df['adsid_count_hits'] = total_df['adsid_count_watch'] * total_df['in_hits']
    total_df['adsid_count_visits'] = total_df['adsid_count_hits'] * total_df['in_visits']

    total_df['partnerprice_watch'] = total_df['partnerprice'] * total_df['in_watch']
    total_df['partnerprice_hits'] = total_df['partnerprice_watch'] * total_df['in_hits']
    total_df['partnerprice_visits'] = total_df['partnerprice_hits'] * total_df['in_visits']

    total_df = total_df.merge(page_counters[['page_id', 'domain']], on="page_id")
    total_df['page'] = total_df['page_id'].map(str) + ' (' + total_df['domain'] + ')'

    dump_table(opts.date_start, total_df)

    total_df.drop(columns=['in_visits', 'in_hits', 'in_watch', 'adsessionid', 'page_id', 'domain'], inplace=True)

    # --------------Daily data--------------------
    total_df_aggr = total_df.groupby(['ismobile', 'osfamily', 'osname', 'osversion', 'page']).sum().reset_index()

    total_df_aggr["fielddate"] = opts.date_start

    total_df_aggr["ismobile"] = total_df_aggr["ismobile"].map(lambda x: 'Mobile' if x == 'true' else 'Desktop' if x == 'false' else x)

    categories = ['ismobile', 'osfamily', 'osname', 'osversion']
    other_fields = ['page', 'fielddate']

    total_df_aggr_with_subtotals = add_subtotals(total_df_aggr, categories, other_fields)
    return total_df_aggr_with_subtotals
