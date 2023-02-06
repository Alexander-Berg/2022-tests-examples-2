
# coding: utf-8

# In[1]:



#!/usr/bin/python
import re
import json
import urllib
import urllib2
import StringIO
import datetime
import pandas as pd
import os
import time
import numpy as np
import json
pd.set_option('display.max_colwidth', 5000)

from urllib import quote
from yql.api.v1.client import YqlClient


# In[3]:


import datetime
import requests
from io import StringIO
import pandas as pd

from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly import graph_objs as go
import requests
import StringIO
import pandas as pd

print __version__ # need 1.9.0 or greater

init_notebook_mode(connected = True)
import numpy as np


def plotly_df(df, name_table = 'test.html', title='', xTitle=None, yTitle=None):
    data = []
    print name_table
    
    if type(df) == pd.Series:
        df = pd.DataFrame(df)

    for column in df.columns:
        trace = go.Scatter(
            x=df.index,
            y=df[column],
            mode='lines',
            name=column,
        )
        data.append(trace)
    layout = dict(title=title,  xaxis=dict(title=xTitle), yaxis=dict(title=yTitle))
    fig = dict(data=data, layout=layout)
    
    iplot(fig, show_link=False)
    print name_table
    with open(name_table,'w') as f:
        f.write(plot(fig, show_link=False, output_type='div', include_plotlyjs=True))

    
def determine_thematic(thematic):
    if thematic in thematics:
        return thematic
    else:
        return 'other'

pd.DataFrame.plotly = plotly_df
pd.Series.plotly = plotly_df


# In[4]:


def get_config():
    with open('../my_config.json') as f:
        config_data = f.read()
    config = json.loads(config_data)
    return config


YQL_TOKEN = get_config()['YQL_TOKEN']
STATFACE_TOKEN = get_config()['STATFACE_TOKEN']
import requests
import json

def run_yql_wait_and_return(yql_query, db = 'hahn'):
    client = YqlClient(db='hahn', token = get_config()['YQL_TOKEN'])

    request = client.query(yql_query.decode('utf8'))
    request.run()
    result = request.get_results()

    result_content = json.loads(result.result._content)

    return request.full_dataframe


# In[6]:


def df_to_wiki(df, show_index = False):
    print '#|\n ||' + df.to_csv(index = show_index, sep = '|').replace('|', ' | ').replace('\n', '|| \n ||')[:-2] + '|#'


# #### Тут захордкожены хосты прода и теста:

# In[7]:


TEST_HOST = 'http://mtlog01-01-1t.yandex.ru:8123'
PROD_HOST = 'http://mtlog01-01-1.yandex.ru:8123'

YQL_TOKEN = get_config()['YQL_TOKEN']
STATFACE_TOKEN = get_config()['STATFACE_TOKEN']
CH_USER = get_config()['CH_USER']
CH_PASSWORD = get_config()['CH_PASSWORD']
import requests
def get_clickhouse_data(query, host, connection_timeout = 1500):
    NUMBER_OF_TRIES = 30
    DELAY = 10
#    print query
    for i in range(NUMBER_OF_TRIES):
        r = requests.post(host, data = query, timeout=connection_timeout, auth=(CH_USER, CH_PASSWORD))
        if r.status_code == 200:
            return r.text
        else:
            print 'ATTENTION: try #%d failed' % i
            if i != (NUMBER_OF_TRIES-1):
                print query
                print r.text
                time.sleep(DELAY*(i+1))
            else:
                raise ValueError, r.text 


def get_clickhouse_df(query, host, connection_timeout = 1500):
    data = get_clickhouse_data(query, host, connection_timeout) 
    df = pd.read_csv(StringIO.StringIO(data), sep = '\t')
    return df


# ### Таблицы

# In[8]:


TRAFIC_SOURCE = '''
    SELECT
        TraficSourceID,
        dictGetString('TraficSource', 'value', tuple(toInt8(TraficSourceID))) AS TraficSourceName,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
    GROUP BY TraficSourceID
    ORDER BY TraficSourceID
    
    FORMAT TabSeparatedWithNames
'''

SEARCH_ENGINE = '''
    SELECT
        SearchEngineID,
        dictGetString('SearchEngine', 'value', toUInt64(SearchEngineID)) AS SearchEngineName,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        AND TraficSourceID == 2
        {layer}
    GROUP BY SearchEngineID
    ORDER BY SearchEngineID
    
    FORMAT TabSeparatedWithNames
    '''

RECOMENDATION = '''
    SELECT
        RecommendationSystemID,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        AND TraficSourceID == 9
        {layer}
    GROUP BY RecommendationSystemID
    ORDER BY RecommendationSystemID
    
    FORMAT TabSeparatedWithNames
    '''

MESSENGER = '''
    SELECT
        MessengerID,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        AND TraficSourceID == 10
        {layer}
    GROUP BY MessengerID
    ORDER BY MessengerID
    
    FORMAT TabSeparatedWithNames
    '''

OS = '''
    SELECT
        dictGetString('OS', 'value', toUInt64(OS)) AS OSName,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
    GROUP BY OSName
    ORDER BY visits DESC
    
    FORMAT TabSeparatedWithNames
    '''

PARENTSOS = '''
    SELECT
        dictGetString('OS', 'value', dictGetUInt64('OS', 'ParentId', toUInt64(OS))) as ParentOSName,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
    GROUP BY ParentOSName
    ORDER BY visits DESC
    
    FORMAT TabSeparatedWithNames
    '''


UserAgent = '''
    SELECT
        dictGetString('UserAgent', 'value', toUInt64(UserAgent)) as UserAgentName,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
    GROUP BY UserAgentName
    ORDER BY visits DESC
    
    FORMAT TabSeparatedWithNames'''


# In[9]:


def load_data(query, indexes, date1, date2, start_time, end_time, HOST, layer = ''):
    q = query.format(
        date1 = date1.strftime('%Y-%m-%d'),
        date2 = date2.strftime('%Y-%m-%d'),
        start_time = start_time,
        end_time = end_time,
        layer = layer
    )
#    print q
    return get_clickhouse_df(q, HOST).set_index(indexes)


def compare_data(query, indexes, date1, date2, start_time, end_time):
    test_df = load_data(query, indexes, date1, date2, start_time, end_time, TEST_HOST)
    TOTAL_TRAFFIC = sum(list(test_df.visits))
    test_df['share'] = map(lambda x: 100 * round(float(x) / TOTAL_TRAFFIC, 4), test_df['visits'])
    
    prod_df_1 = load_data(query, indexes, date1, date2, start_time, end_time, PROD_HOST, layer = '''AND toInt32(substring(hostName(), 6, 2)) == 1 ''')
    TOTAL_TRAFFIC = sum(list(prod_df_1.visits))
    prod_df_1['share'] = map(lambda x: 100 * round(float(x) / TOTAL_TRAFFIC, 4), prod_df_1['visits'])
    
    prod_df = load_data(query, indexes, date1, date2, start_time, end_time, PROD_HOST)
    TOTAL_TRAFFIC = sum(list(prod_df.visits))
    prod_df['share'] = map(lambda x: 100 * round(float(x) / TOTAL_TRAFFIC, 4), prod_df['visits'])
    
#    return test_df.join(prod_df, rsuffix = '_prod')

    res_df = test_df.join(prod_df_1, rsuffix = '_prod', how = 'outer').join(prod_df, rsuffix = '_prod_full', how = 'outer')[['visits', 'visits_prod', 'visits_prod_full', 'share', 'share_prod', 'share_prod_full']].fillna(0)
    res_df['diff'] = map(lambda x, y: x - y,  res_df.share, res_df.share_prod)
    res_df['diff_2'] = map(lambda x, y: x - y,  res_df.share, res_df.share_prod_full)
    
    res_df['visits'] = map(int, res_df['visits'])
    res_df['visits_prod'] = map(int, res_df['visits_prod'])
    for key in ['share', 'share_prod', 'share_prod_full', 'diff', 'diff_2']:
        res_df[key] = map(lambda x: round(float(x), 2), res_df[key])

    return res_df.sort_values('visits_prod_full', ascending = False)[['visits', 'visits_prod', 'share', 'share_prod', 'share_prod_full', 'diff', 'diff_2']]


# In[10]:


today = datetime.datetime.today()
date1, date2 = datetime.datetime(2019, 9, 10), datetime.datetime(2019, 9, 16)
start_time = '2019-09-11 14:00:00'
end_time = '2019-09-16 06:00:00'


# In[11]:


compare_trafic_source_df = compare_data(TRAFIC_SOURCE, ['TraficSourceID', 'TraficSourceName'], date1, date2, start_time, end_time)
print 'visits_TEST =', sum(list(compare_trafic_source_df.visits))
print 'visits_PROD =', sum(list(compare_trafic_source_df.visits_prod))
compare_trafic_source_df


# In[12]:


search_df = compare_data(SEARCH_ENGINE, ['SearchEngineID', 'SearchEngineName'], date1, date2, start_time, end_time)
print 'visits_TEST =', sum(list(search_df.visits))
print 'visits_PROD =', sum(list(search_df.visits_prod))

search_df.head(20)


# In[13]:


rec_df = compare_data(RECOMENDATION, ['RecommendationSystemID'], date1, date2, start_time, end_time)
rec_df.head(20)


# In[14]:


messenger_df = compare_data(MESSENGER, ['MessengerID'], date1, date2, start_time, end_time)
messenger_df.head(20)


# In[15]:


compare_parent_os_df = compare_data(PARENTSOS, ['ParentOSName'], date1, date2, start_time, end_time)
print 'visits_TEST =', sum(list(compare_parent_os_df.visits))
print 'visits_PROD =', sum(list(compare_parent_os_df.visits_prod))
compare_parent_os_df.head(10)


# In[16]:


compare_os_df = compare_data(OS, ['OSName'], date1, date2, start_time, end_time)
print 'visits_TEST =', sum(list(compare_os_df.visits))
print 'visits_PROD =', sum(list(compare_os_df.visits_prod))
compare_os_df.head(10)


# In[17]:


compare_useragent_df = compare_data(UserAgent, ['UserAgentName'], date1, date2, start_time, end_time)
print 'visits_TEST =', sum(list(compare_useragent_df.visits))
print 'visits_PROD =', sum(list(compare_useragent_df.visits_prod))
compare_useragent_df.head(10)


# ### Графики

# In[18]:


PLOT_TRAFFIC = '''
    SELECT
        time,
        TraficSourceName,
        visits,
        total_visits,
        100 * round(visits / total_visits, 4) as share
    FROM
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        dictGetString('TraficSource', 'value', tuple(toInt8(TraficSourceID))) AS TraficSourceName,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
    GROUP BY time, TraficSourceID)
    
    ANY LEFT JOIN
    
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        sum(Sign) as total_visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
    GROUP BY time)
    
    USING (time)
    
    FORMAT TabSeparatedWithNames
    '''


PLOT_SEARCH = '''
    SELECT
        time,
        visits,
        total_visits,
        'YANDEX' as name,
        100 * round(visits / total_visits, 4) as share
    FROM
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
        AND TraficSourceID = 2
        AND dictGetUInt64('SearchEngine', 'ParentId', toUInt64(SearchEngineID)) == 26
    GROUP BY time, TraficSourceID)
    
    ANY LEFT JOIN
    
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        sum(Sign) as total_visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
        AND TraficSourceID = 2
    GROUP BY time)
    
    USING (time)
    
    FORMAT TabSeparatedWithNames
    '''


PLOT_ZEN = '''
    SELECT
        time,
        visits,
        total_visits,
        RecommendationSystemID,
        100 * round(visits / total_visits, 4) as share
    FROM
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        RecommendationSystemID,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
        AND TraficSourceID = 9
    GROUP BY time, TraficSourceID, RecommendationSystemID)
    
    ANY LEFT JOIN
    
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        sum(Sign) as total_visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
        AND TraficSourceID = 9
    GROUP BY time)
    
    USING (time)
    
    FORMAT TabSeparatedWithNames
    '''


PLOT_DIRECT = '''
    SELECT
        time,
        AdvEngineName,
        visits,
        total_visits,
        100 * round(visits / total_visits, 4) as share
    FROM
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        dictGetString('AdvEngine', 'value', toUInt64(AdvEngineID)) as AdvEngineName,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
        AND TraficSourceID = 3
        AND AdvEngineID IN (1, 2, 81, 38, 12, 66, 48, 37, 76, 56, 46)
    GROUP BY time, TraficSourceID, AdvEngineID)
    
    ANY LEFT JOIN
    
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        sum(Sign) as total_visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        {layer}
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        AND TraficSourceID = 3
    GROUP BY time)
    
    USING (time)
    
    FORMAT TabSeparatedWithNames
    '''

PLOT_OS = '''
    SELECT
        time,
        OSName,
        ParentOSName,
        visits,
        total_visits,
        100 * round(visits / total_visits, 4) as share
    FROM
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        dictGetString('OS', 'value', toUInt64(OS)) AS OSName,
        dictGetUInt64('OS', 'ParentId', toUInt64(OS)) AS ParentOS,
        dictGetString('OS', 'value', ParentOS) as ParentOSName,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
        AND ParentOS IN (108, 106)
        AND OS >= 237
    GROUP BY time, OS)
    
    ANY LEFT JOIN
    
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        sum(Sign) as total_visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        {layer}
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
    GROUP BY time)
    
    USING (time)
    
    order by time
    
    FORMAT TabSeparatedWithNames'''


PLOT_USERAGENT = '''
    SELECT
        time,
        UserAgentName,
        visits,
        total_visits,
        100 * round(visits / total_visits, 4) as share
    FROM
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        dictGetString('UserAgent', 'value', toUInt64(UserAgent)) as UserAgentName,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
        AND UserAgent IN (6, 83, 70, 38, 117, 72, 190, 3, 2, 191, 135)
    GROUP BY time, UserAgentName)
    
    ANY LEFT JOIN
    
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        sum(Sign) as total_visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        {layer}
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
    GROUP BY time)
    
    USING (time)
    
    order by time
    
    FORMAT TabSeparatedWithNames'''



PLOT_USERAGENTNEW = '''
    SELECT
        time,
        UserAgentName,
        visits,
        total_visits,
        100 * round(visits / total_visits, 4) as share
    FROM
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        dictGetString('UserAgent', 'value', toUInt64(UserAgent)) as UserAgentName,
        sum(Sign) as visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
        {layer}
        AND UserAgent >= 198
    GROUP BY time, UserAgentName)
    
    ANY LEFT JOIN
    
    (SELECT
        toStartOfFiveMinute(StartTime) as time,
        sum(Sign) as total_visits
    FROM visits_all
    WHERE StartDate >= '{date1}' AND StartDate <= '{date2}'
        {layer}
        AND StartTime >= '{start_time}' AND StartTime <= '{end_time}'
    GROUP BY time)
    
    USING (time)
    
    order by time
    
    FORMAT TabSeparatedWithNames'''


def load_traffic_sources_2(query, date1, date2, start_time, end_time, HOST, layer=''):
    q = query.format(
        date1 = date1.strftime('%Y-%m-%d'),
        date2 = date2.strftime('%Y-%m-%d'),
        start_time = start_time,
        end_time = end_time,
        layer = layer
    )
#    print q
    return get_clickhouse_df(q, HOST)


def plot_trafic_source(query, name, date1, date2, start_time, end_time, name_table = 'Test.html', title = ''):
    df = load_traffic_sources_2(query, date1, date2, start_time, end_time, TEST_HOST)
    print df.columns
    
    prod_df = load_traffic_sources_2(query, date1, date2, start_time, end_time, PROD_HOST, layer = '''AND toInt32(substring(hostName(), 6, 2)) == 1 ''')
#    print df.columns

    df_2 = df.pivot_table(index = 'time', columns = name, values = 'share').join(prod_df.pivot_table(index = 'time', columns = name, values = 'share'), rsuffix = '_CONTROL')
    df_2.plotly(name_table = name_table, title = title)

    return df, prod_df


# In[19]:


#график доли трафика 
today = datetime.datetime.today()
date1, date2 = datetime.datetime(2019, 9, 10), datetime.datetime(2019, 9, 16)
start_time = '2019-09-12 16:45:00'
end_time = '2019-09-16 06:00:00'
res, res_2 = plot_trafic_source(PLOT_TRAFFIC, 'TraficSourceName', date1, date2, start_time, end_time, name_table = 'TS.html', title = 'Доли источников, %.')


# In[20]:


res[res.TraficSourceName == 'Прямые заходы'].sort_values('time').set_index('time')[['total_visits']].plotly(name_table = 'abs.html', title = 'Визиты на тесте, абсолюты')


# In[21]:


res, res_2 = plot_trafic_source(PLOT_SEARCH, 'name', date1, date2, start_time, end_time, name_table = 'Yandex.html', title = 'Доля Яндекса в поиске, %.')


# In[22]:


res, res_2 = plot_trafic_source(PLOT_ZEN, 'RecommendationSystemID', date1, date2, start_time, end_time, name_table = 'Zen.html', title = 'Доля Дзена в рекомендациях, %.')


# In[23]:


res, res_2 = plot_trafic_source(PLOT_DIRECT, 'AdvEngineName', date1, date2, start_time, end_time, name_table = 'Agv.html', title = 'Доля топа рекламных систем, %.')


# In[24]:


res, res_2 = plot_trafic_source(PLOT_USERAGENT, 'UserAgentName', date1, date2, start_time, end_time, name_table = 'UserAgent.html', title = 'Доля топа UserAgent, %')


# In[25]:


res, res_2 = plot_trafic_source(PLOT_USERAGENTNEW, 'UserAgentName', date1, date2, start_time, end_time, name_table = 'UserAgentNew.html', title = 'Доля свежих UserAgent, %')


# In[26]:


res, res_2 = plot_trafic_source(PLOT_OS, 'OSName', date1, date2, start_time, end_time, name_table = 'OS.html', title = 'Доля свежих Android и iOS в общем трафике, %.')


# ### Отладка

# In[27]:


#для отладки топа в разных срезах
q = '''
    SELECT
        UserAgent,
        dictGetString('UserAgent', 'value', toUInt64(UserAgent)) as UserAgentName,
        sum(Sign) as visits
    FROM visits_all sample 1/100
    WHERE StartDate >= '2019-09-09'
        AND TraficSourceID = 3
    GROUP BY UserAgent
    ORDER BY visits DESC
    
    FORMAT TabSeparatedWithNames'''
top_df =  get_clickhouse_df(q, PROD_HOST)
top_df.head()


# In[28]:


#for i in re.head(11).UserAgent:
#    print str(i) + ',',


# ### Словари в mysql

# In[29]:


MYSQL_USER = get_config()['mysql_login']
MYSQL_PASS = get_config()['mysql_password']

import mysql.connector
from mysql.connector.errors import Error

def convert_to_string(string):
    if isinstance(string, unicode):
        try:
            return string.encode('utf8')
        except:
            print 
            return str(string)
    else:
        return str(string)

def conv_main(query, header=True):
    """
    Простенькая функция для mysql. По дефолту идет в базу conv_main. Можно выключить заголовок
    """
    db = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PASS, host="mtacs01et", port=3310, database='conv_main', charset='utf8')
    cursor = db.cursor()
    cursor.execute(query)
    all_data = cursor.fetchall()
    field_names = map(lambda x: x.encode('utf-8'), [i[0] for i in cursor.description])
    data = '\n'.join(['\t'.join([convert_to_string(item) for item in one]) for one in all_data])
    if header:
        data = '\t'.join(field_names) + '\n' + data
    return data


# In[30]:


q = '''
show tables
'''
mysql_df = pd.read_csv(StringIO.StringIO(conv_main(q)), sep='\t')
mysql_df.head()


# In[31]:


q = '''
select 
    *
from RecommendationSystems
'''
recommendation_df = pd.read_csv(StringIO.StringIO(conv_main(q)), sep='\t')
recommendation_df


# In[32]:


q = '''
select 
    *
from Messengers
'''
messenger_df = pd.read_csv(StringIO.StringIO(conv_main(q)), sep='\t')
messenger_df


# ### Для wiki

# In[33]:


def to_wiki(df, title):
    print '<{' + title
    df_to_wiki(df, show_index = True)
    print '}>'


# In[34]:


compare_trafic_source_df.head()


# In[35]:


to_wiki(compare_trafic_source_df, 'Источники трафика')
to_wiki(search_df.head(10), 'Поисковые системы')
to_wiki(rec_df, 'Рекомендательные системы')
to_wiki(messenger_df, 'Мессенджеры')
to_wiki(compare_parent_os_df.head(), 'Основные OS')
to_wiki(compare_os_df.head(10), 'OS')
to_wiki(compare_useragent_df.head(10), 'UserAgent')

