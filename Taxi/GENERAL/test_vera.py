

# coding: utf-8

# In[1]:
from business_models import hahn, greenplum

# In[1]:
greenplum.replicate(yt_path='//home/taxi-analytics/deynega/cron/bb_tableau', 
                    table_name='analyst.deynega_bb_tableau', with_grant=True, operator='select', to='analyst')

# In[1]:
greenplum.replicate(yt_path='//home/taxi-analytics/deynega/cron/bb_tableau_borders', 
                    table_name='analyst.deynega_bb_tableau_borders', with_grant=True, operator='select', to='analyst')

# In[1]:
print('ok')
