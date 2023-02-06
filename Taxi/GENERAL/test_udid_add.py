#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pandas as pd
import numpy as np
import os
from copy import copy
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from yql.api.v1.client import YqlClient
import business_models as bm
from business_models import gdocs_helper
import time
from business_models import hahn, greenplum
from collections import Counter
import requests
import json
import warnings
warnings.filterwarnings('ignore')


# In[2]:


script = '''
USE `hahn`;
use hahn;
pragma yt.InferSchema;
pragma SimpleColumns;
pragma yson.DisableStrict;
pragma yt.DefaultMemoryLimit = '8G';
$dr_phone = (
SELECT old_unique_driver_id, FirstName,MiddleName,LastName, utc_created_dttm, phone_pd_id_list
FROM (
select 
    old_unique_driver_id
    , utc_created_dttm
    , first_name as FirstName, middle_name as MiddleName, last_name as LastName
    , Yson::ConvertToStringList(phone_pd_id_list) as phone_pd_id_list
from 
    `//home/taxi-dwh/cdm/supply/dim_executor_profile_act/dim_executor_profile_act` as b)
FLATTEN BY phone_pd_id_list
);
SELECT 
    phone_pd_id, lead_id
    , MAX_BY(FirstName,b.utc_created_dttm) as FirstName
    , MAX_BY(MiddleName,b.utc_created_dttm) as MiddleName
    , MAX_BY(LastName,b.utc_created_dttm) as LastName
    , MAX_BY(old_unique_driver_id,b.utc_created_dttm) as unique_driver_id
from
    `//home/taxi-dwh/ods/salesforce/lead/lead` as a 
    INNER JOIN $dr_phone as b
        ON a.phone_pd_id = b.phone_pd_id_list
where 
    1=1
    --and executor_profile_id is null
    and old_unique_driver_id is not null 
GROUP BY a.phone_pd_id as phone_pd_id, a.lead_id as lead_id;
insert into `//home/taxi-analytics/anyamalkova/salesforce_lead_debug/df` with truncate 
select * from $dr_phone;'''
df = hahn(script,syntax_version=1.0)
df = bm.change_coding(df)


# In[6]:


# Получение токена
url = 'https://login.salesforce.com/services/oauth2/token'

payload = {
        'grant_type':'password',
        'client_id': bm.config_holder.ConfigHolder().SF_client_id,
        'client_secret':bm.config_holder.ConfigHolder().SF_client_secret,
        'username':'robot-sf-analytics@yandex-team.ru',
        'password':bm.config_holder.ConfigHolder().SF_password
}
q = requests.post(url,data=payload)


# In[35]:


url = 'https://yandextaxi.my.salesforce.com/services/data/v48.0/jobs/query'
data = {
    "operation": "query",
    "query": "SELECT Id, RecordTypeId, DriverId__c FROM Lead"
                }
headers = {'Authorization':u'Bearer '+q.json()[u'access_token'],
           "Accept": "application/json",
 "Content-Type": "application/json; charset=UTF-8"}
S = requests.post(url,
                  headers=headers,
                  data=json.dumps(data))
bulk_id = S.json()['id']


locator = '0'
while locator != 'null':
    check = False
    check2 = 0
    while (check != True) & (check2 < 3):
        try:
            url = 'https://yandextaxi.my.salesforce.com/services/data/v48.0/jobs/query/'+bulk_id+'/results?locator='+locator
            headers = {'Authorization':u'Bearer '+q.json()[u'access_token'],
                       "Accept": "application/json",
                       "Content-Type": "application/json; charset=UTF-8"}
            S_get = requests.get(url,headers=headers)
            if S_get.status_code == 200:
                print S_get.headers['Sforce-Locator']
                text_file = open(bulk_id+".txt", "a")
                n = text_file.write(S_get.content.replace('\",\"',';;;').replace('\"',''))
                text_file.close()
                locator = S_get.headers['Sforce-Locator']
                check = True
            else:
                check2 += 1
        except:
            print 'Error soql', S_get.status_code
            check2 += 1
leads = pd.read_csv(bulk_id+".txt",sep=';;;',encoding='utf-8')
leads = leads[leads.Id != 'Id']
leads.drop_duplicates(inplace=True)
os.remove(bulk_id+".txt")

hahn.write(
    leads,
    '//home/taxi-analytics/anyamalkova/salesforce_lead_debug/leads'
)


df.rename(columns={'lead_id':'Id'},inplace=True)
res = pd.merge(leads,df[['Id','unique_driver_id','FirstName','MiddleName','LastName']],how='inner',on=['Id'])
res = res[res.DriverId__c.isna()]

hahn.write(
    res,
    '//home/taxi-analytics/anyamalkova/salesforce_lead_debug/res'
)


# In[27]:


res['DriverId__c'] = res['unique_driver_id']
res = res[['Id','DriverId__c','FirstName','MiddleName','LastName']].drop_duplicates()

hahn.write(
    res, 
    '//home/taxi-analytics/anyamalkova/salesforce_lead_debug/res_wo_duplicates'
)
# In[29]:


# 1 bulk
url = 'https://yandextaxi.my.salesforce.com/services/data/v48.0/jobs/ingest/'
data = {
    "object" : "Lead",
    "externalIdFieldName":"Id",
    "contentType" : "CSV",
    "operation" : "upsert"
                  }
headers = {'Authorization':u'Bearer '+q.json()[u'access_token'],
           "Accept": "application/json",
 "Content-Type": "application/json; charset=UTF-8"}


S = requests.post(url,
                  headers=headers,
                  data=json.dumps(data))
bulk_id = S.json()['id']

res.to_csv('tmp_ops.txt',sep=',',index=None,encoding='utf-8')
f = open("tmp_ops.txt", "r")
CSV = f.read()

url = 'https://yandextaxi.my.salesforce.com/services/data/v48.0/jobs/ingest/'+bulk_id+'/batches/'
headers = {'Authorization':u'Bearer '+q.json()[u'access_token'],
           "Accept": "application/json",
             "Content-Type": "text/csv"}
S_put = requests.put(url,headers=headers,data=CSV)

url = 'https://yandextaxi.my.salesforce.com/services/data/v48.0/jobs/ingest/'+bulk_id
headers = {'Authorization':u'Bearer '+q.json()[u'access_token'],
           "Accept": "application/json",
 "Content-Type": "application/json; charset=UTF-8"}
S_close = requests.patch(url,headers=headers,data=json.dumps({"state" : "UploadComplete"}))

os.remove('tmp_ops.txt')


# In[30]:


print 1
