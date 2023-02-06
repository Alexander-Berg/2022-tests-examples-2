# -*- coding: utf-8 -*-k

from metr_utils.databases import yql_db
from metr_utils import generate_query
from datetime import datetime

QUERY = '''
SELECT * from `home/metrica-analytics/.tmp/logs/rsya_money_join_bad_adsids/{date_start}_testing`
'''


def get_data(opts):
    query_full = generate_query.get_query(QUERY)
    total_df = yql_db.get_df(query=query_full)

    hour_df_aggr = total_df.rename(index=str, columns={"hour": "fielddate"}).groupby(['fielddate', 'page']).sum().reset_index()

    hour_df_aggr['ismobile'] = 'Total'
    hour_df_aggr['osfamily'] = 'Total'
    hour_df_aggr['osname'] = 'Total'
    hour_df_aggr['osversion'] = 'Total'
    hour_df_aggr['fielddate'] = hour_df_aggr['fielddate'].apply(datetime.fromtimestamp).astype(str)
    return hour_df_aggr
