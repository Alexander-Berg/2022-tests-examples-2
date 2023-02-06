amocrm:
  connections:
    default:
      domain: https://yandextaxi.amocrm.ru
      user_hash: {{ AMOCRM_DEFAULT['user_hash'] }}
      user_login: {{ AMOCRM_DEFAULT['user_login'] }}
direct:
  connections:
    taxi:
      yndx-direct-taxi:
        token: {{ DIRECT_TAXI['yndx-direct-taxi'] }}
        type: client
      yndx-taxi-promo:
        token: {{ DIRECT_TAXI['yndx-taxi-promo'] }}
        type: agency
    food:
      yndx-robot-eda-metrika:
        token: {{ DIRECT_FOOD['yndx-robot-eda-metrika'] }}
        type: agency
adwords:
  connections:
    taxi:
      adwords_client_config:
        client_id: {{ GOOGLEADS_ADWORDS_TAXI_CLIENT['client_id'] }}
        client_secret: {{ GOOGLEADS_ADWORDS_TAXI_CLIENT['client_secret'] }}
        developer_token: {{ GOOGLEADS_ADWORDS_TAXI_CLIENT['developer_token'] }}
        refresh_token: {{ GOOGLEADS_ADWORDS_TAXI_CLIENT['refresh_token'] }}
        user_agent: {{ GOOGLEADS_ADWORDS_TAXI_CLIENT['user_agent'] }}
    food:
      adwords_client_config:
        client_id: {{ GOOGLEADS_ADWORDS_FOOD_CLIENT['client_id'] }}
        client_secret: {{ GOOGLEADS_ADWORDS_FOOD_CLIENT['client_secret'] }}
        developer_token: {{ GOOGLEADS_ADWORDS_FOOD_CLIENT['developer_token'] }}
        refresh_token: {{ GOOGLEADS_ADWORDS_FOOD_CLIENT['refresh_token'] }}
        user_agent: {{ GOOGLEADS_ADWORDS_FOOD_CLIENT['user_agent'] }}
mongodb:
  connections:
    corben: "{{ MONGODB['corben'] }}"
    dbantifraud: "{{ MONGODB['dbantifraud'] }}"
    dbarchive: "{{ MONGODB['dbarchive'] }}"
    dbbilling: "{{ MONGODB['dbbilling'] }}"
    dbcars: "{{ MONGODB['dbcars'] }}"
    dbcorp: "{{ MONGODB['dbcorp'] }}"
    dbdrivers: "{{ MONGODB['dbdrivers'] }}"
    dbexams: "{{ MONGODB['dbexams'] }}"
    dblogs: "{{ MONGODB['dblogs'] }}"
    dbmisc: "{{ MONGODB['dbmisc'] }}"
    dbparks: "{{ MONGODB['dbparks'] }}"
    dbpinstats: "{{ MONGODB['dbpinstats'] }}"
    dbprocessing: "{{ MONGODB['dbprocessing'] }}"
    dbreferral: "{{ MONGODB['dbreferral'] }}"
    dbsubvention_reasons: "{{ MONGODB['dbsubvention_reasons'] }}"
    dbtaxi: "{{ MONGODB['dbtaxi'] }}"
    dbtracks: "{{ MONGODB['dbtracks'] }}"
    dbusers: "{{ MONGODB['dbusers'] }}"
    gprstimings: "{{ MONGODB['gprstimings'] }}"
    qc: "{{ MONGODB['qc'] }}"
    stats: "{{ MONGODB['stats'] }}"
    dbfeedback: "{{ MONGODB['dbfeedback'] }}"
mqc:
  connections:
    default:
      host: 'https://taxiqc.ru/oauth/token'
      password: {{ MQC_DEFAULT['password'] }}
      user: {{ MQC_DEFAULT['username'] }}
mysql:
  connections:
    bigfood:
      database: bigfood
      host: infra.eda.yandex.net
      password: {{ MYSQL_BIGFOOD['password'] }}
      port: 3306
      user: {{ MYSQL_BIGFOOD['user'] }}
    analytics:
      database: analytics
      host: infra.eda.yandex.net
      password: {{ MYSQL_ANALYTICS['password'] }}
      port: 3307
      user: {{ MYSQL_ANALYTICS['user'] }}
    food_selectel:
      database: u486941_city_all
      host: grafik-test.foodfox.ru
      password: {{ MYSQL_FOOD_SELECTEL['password'] }}
      port: 3307
      user: {{ MYSQL_FOOD_SELECTEL['user'] }}
    eda_staging_kenobi:
      database: bigfood_staging
      host: 2a02:6b8:c08:bb15:0:43cb:6860:0
      password: {{ MYSQL_EDA_STAGING_KENOBI['password'] }}
      port: 3306
      user: {{ MYSQL_EDA_STAGING_KENOBI['user'] }}
    testing:
      database: taxi_test_dwh_etl
      host: c-mdb8hj5hjrh0evi80lpj.rw.db.yandex.net
      password: {{ MYSQL_ETL_TESTING['password'] }}
      port: 3306
      user: {{ MYSQL_ETL_TESTING['user'] }}
mssql:
  connections:
    chef:
      host: {{ MSSQL_CHEF['host'] }}
      port: {{ MSSQL_CHEF['port'] }}
      user: {{ MSSQL_CHEF['login'] }}
      password: {{ MSSQL_CHEF['password'] }}
oktell:
  connections:
    default:
      database: oktell
      host: octell-data.yadrivers.com
      password: {{ OKTELL_DEFAULT['password'] }}
      port: 1433
      user: {{ OKTELL_DEFAULT['user'] }}
    users:
      - host: octell-data.yadrivers.com
        port: 1433
        database: oktell
        user: {{ OKTELL_USERS['host1_username'] }}
        password: {{ OKTELL_USERS['host1_password'] }}
      - host: octellmssql2.yadrivers.com
        port: 1433
        database: oktell
        user: {{ OKTELL_USERS['host2_username'] }}
        password: {{ OKTELL_USERS['host2_password'] }}
      - host: octellmssql3.yadrivers.com
        port: 1433
        database: oktell
        user: {{ OKTELL_USERS['host3_username'] }}
        password: {{ OKTELL_USERS['host3_password'] }}
    hiring:
      - host: 2a00:ab00:1203:16::2
        port: 1433
        database: oktell
        user: {{ OKTELL_HIRING['user'] }}
        password: {{ OKTELL_HIRING['password'] }}
ssas:
  connections:
    default:
      SSAS_URL: http://taxi-ssas-dev.ld.yandex.ru/YandexOlap/
      greenplum_user: {{ SSAS_DEFAULT['greenplum_user'] }}
      greenplum_password: {{ SSAS_DEFAULT['greenplum_password'] }}
      greenplum_host: gpdb-pgbouncer.taxi.yandex.net
googledocs:
  connections:
    taxidwh:
      client_id: {{ GOOGLE_DOCS_DWH['client_id'] }}
      client_secret: {{ GOOGLE_DOCS_DWH['client_secret'] }}
      refresh_token: {{ GOOGLE_DOCS_DWH['refresh_token'] }}
startrek:
  connections:
    taxidwh:
      token: {{ STARTREK_TAXIDWH['token'] }}
      useragent: robot-taxi-stat
statface:
  connections:
    taxidwh:
      token: {{ STATFACE_TAXIDWH['token'] }}
taximeter:
  connections:
    misc:
    - database: taximeter_db_misc_shard1
      host: c-9c346763-601c-44cf-a85b-a09ecd9c2592.ro.db.yandex.net
      password: {{ TAXIMETER_DB_MISC['shard1_password'] }}
      port: 6432
      user: {{ TAXIMETER_DB_MISC['shard1_username'] }}
    orders: # one shard of 16
    - database: taximeter_db_orders_shard1
      host: c-ce79924a-08d0-48a9-8cec-3044eb740220.ro.db.yandex.net
      password: {{ TAXIMETER_DB_ORDERS['shard1_password'] }}
      port: 6432
      user: {{ TAXIMETER_DB_ORDERS['shard1_username'] }}
    payments: # one shard of 4
    - database: taximeter_db_payments_shard1
      host: c-a24174a1-d836-413e-93ef-8febdd5a2e43.ro.db.yandex.net
      password: {{ TAXIMETER_DB_PAYMENTS['shard1_password'] }}
      port: 6432
      user: {{ TAXIMETER_DB_PAYMENTS['shard1_username'] }}
    feedbacks: # one shard of 2
    - database: taximeter_db_feedbacks_shard0
      host: c-9c523d56-37b8-433f-ba81-f2b631fa1257.ro.db.yandex.net
      password: {{ TAXIMETER_DB_FEEDBACKS['shard0_password'] }}
      port: 6432
      user: {{ TAXIMETER_DB_FEEDBACKS['shard0_username'] }}
zendesk:
  connections:
    zendesk_food:
      token: {{ ZENDESK_FOOD['token'] }}
      url_prefix: foodfox
      username: {{ ZENDESK_FOOD['username'] }}
    zendesk_hiring:
      token: {{ ZENDESK_HIRING['token'] }}
      url_prefix: yataxinewdrivers
      username: {{ ZENDESK_HIRING['username'] }}
    zendesk_support:
      token: {{ ZENDESK_SUPPORT['token'] }}
      url_prefix: yataxi
      username: {{ ZENDESK_SUPPORT['username'] }}
pgaas:
  connections:
    idm:
      host: sas-iei1dhm20silug2o.db.yandex.net,vla-dcws0d833izs3124.db.yandex.net,man-qw7eq1q5afhpvkee.db.yandex.net
      port: 6432
      database: taxi_test_db_dwhidm_shard0
      user: {{ PGAAS_IDM['username'] }}
      password: {{ PGAAS_IDM['password'] }}
      sslmode: verify-full
      sslrootcert: /etc/yandex/taxi-secdist/pgaas.idm.root.pem
    food: # not prod
      host: myt-ize53ogzdp7e9ci1.db.yandex.net
      port: 6432
      database: eda_couriers_schedule_staging
      user: {{ PGAAS_FOOD['username'] }}
      password: {{ PGAAS_FOOD['password'] }}
      sslmode: verify-full
      sslrootcert: /etc/yandex/taxi-secdist/food.pem
    ctl: # not prod, not read only.
      host: sas-ni3u2q9jmeode21r.db.yandex.net,vla-qrlzhbxr8n30sfyb.db.yandex.net,man-qco1mi6xauy8eted.db.yandex.net
      port: 6432
      database: taxi_test_dwh_ytgpexport
      user: {{ PGAAS_CTL['username'] }}
      password: {{ PGAAS_CTL['password'] }}
      sslmode: verify-full
      sslrootcert: /etc/yandex/taxi-secdist/pgaas.root.pem
      target_session_attrs: read-write
    driver-referrals:
      host: man-sm0msir7y87duiq0.db.yandex.net,sas-dtkzi0lmeqweop4h.db.yandex.net,vla-xtp4w3v81n4hainb.db.yandex.net
      port: 6432
      database: taxi_db_driver_referrals
      user: {{ PGAAS_DRIVER_REFERRALS['username'] }}
      password: {{ PGAAS_DRIVER_REFERRALS['password'] }}
      sslmode: verify-full
      sslrootcert: /etc/yandex/taxi-secdist/pgaas.root.pem
    garage:
      host: man-mdw7qp4n48qg9i82.db.yandex.net,sas-d5jdj1ad7rr4kat0.db.yandex.net,vla-04o4u2d5az06f9lu.db.yandex.net
      port: 6432
      database: taxi_outsource_marketplace_testing
      user: {{ PGAAS_GARAGE['username'] }}
      password: {{ PGAAS_GARAGE['password'] }}
      sslmode: verify-full
      sslrootcert: /etc/yandex/taxi-secdist/pgaas.root.pem
    testing:
      host: sas-ni3u2q9jmeode21r.db.yandex.net,vla-qrlzhbxr8n30sfyb.db.yandex.net,man-qco1mi6xauy8eted.db.yandex.net
      port: 6432
      database: taxi_test_dwh_ytgpexport
      user: {{ PGAAS_YT_GP_EXPORT['user'] }}
      password: {{ PGAAS_YT_GP_EXPORT['password'] }}
      target_session_attrs: read-write
      sslmode: require
    user_referrals:
      host: vla-5mow0ovksq8f8j2k.db.yandex.net,sas-hzzssepvsk53p8bd.db.yandex.net,man-yhs1pim7rxyhluc3.db.yandex.net
      port: 6432
      database: user_referrals
      user: {{ PGAAS_USER_REFERRALS['username'] }}
      password: {{ PGAAS_USER_REFERRALS['password'] }}
      sslmode: verify-full
      sslrootcert: /etc/yandex/taxi-secdist/pgaas.root.pem
    billing_limits:
      host: {{ PGAAS_BILLING_LIMITS['host'] }}
      port: 6432
      database: {{ PGAAS_BILLING_LIMITS['dbname'] }}
      user: {{ PGAAS_BILLING_LIMITS['user'] }}
      password: {{ PGAAS_BILLING_LIMITS['password'] }}
      sslmode: require
    shared_payments:
      host: {{ PGAAS_SHARED_PAYMENTS['host'] }}
      port: 6432
      database: {{ PGAAS_SHARED_PAYMENTS['dbname'] }}
      user: {{ PGAAS_SHARED_PAYMENTS['user'] }}
      password: {{ PGAAS_SHARED_PAYMENTS['password'] }}
      sslmode: require
    lavka_1c:
      host: {{ PGAAS_LAVKA_1C['host'] }}
      port: 6432
      database: {{ PGAAS_LAVKA_1C['db'] }}
      user: {{ PGAAS_LAVKA_1C['user'] }}
      password: {{ PGAAS_LAVKA_1C['password'] }}
      sslmode: require
facebook:
  connections:
    taxi_etl:
      token: {{ FACEBOOK_TAXI['token'] }}
      services:
        Eda-Lavka: {{ FACEBOOK_TAXI['Eda-Lavka'] }}
        uber_az: {{ FACEBOOK_TAXI['uber_az'] }}
        uber_by: {{ FACEBOOK_TAXI['uber_by'] }}
        uber_kz: {{ FACEBOOK_TAXI['uber_kz'] }}
        uber_ru: {{ FACEBOOK_TAXI['uber_ru'] }}
        yandex_taxi: {{ FACEBOOK_TAXI['yandex_taxi'] }}
        yandex_taxi_legacy: {{ FACEBOOK_TAXI['yandex_taxi_legacy'] }}
        yango: {{ FACEBOOK_TAXI['yango'] }}
        Eda-Superapp: {{ FACEBOOK_TAXI['Eda-Superapp'] }}
    eda_etl:
      token: {{ FACEBOOK_FOOD['token'] }}
      services:
        food: {{ FACEBOOK_FOOD['food'] }}
logbroker:
  connections:
    order_proc:
      reader:
        tvm_secret: {{  TVM_taxidwh_lb_order_proc_consumer_testing['tvm_secret']  }}
ftp:
  connections:
    testing:
      host: ftp.yandex.net
      user: {{ FTP_TAXI_DA['testing_username'] }}
      password: {{ FTP_TAXI_DA['testing_password'] }}
snapchat:
  connections:
    taxi-dwh-ads-api:
      adsapi_url: https://adsapi.snapchat.com
      auth_url: https://accounts.snapchat.com
      organization_id: 65d40997-3f61-4511-850a-c0d3640b59a9
      client_id: {{ SNAPCHAT_TAXI_DWH_ADS_API['client_id'] }}
      client_secret: {{ SNAPCHAT_TAXI_DWH_ADS_API['client_secret'] }}
      refresh_token: {{ SNAPCHAT_TAXI_DWH_ADS_API['refresh_token'] }}
taxitelemed:
  connections:
    default:
      host: ytmedtest.inno.co
      headers:
        'X-Client-ID': "{{ TELEMED['client-id'] }}"
        'X-API-Key': "{{ TELEMED['api-key'] }}"
education:
  connections:
    default:
      url: ytaxikiosk.vmb.co
      client_id: {{ EDUCATION_YTAXIKIOSK_VMB_CO['client_id'] }}
      client_secret: {{ EDUCATION_YTAXIKIOSK_VMB_CO['client_secret'] }}
tableau:
  host: tableau-cluster.taxi.tst.yandex-team.ru
  connections:
    tableau-admin:
      site:
      user: robot-taxi-test-user
      password: {{ TABLEAU_ROBOT_TAXI_TEST_USER['password'] }}
    tableau-repository:
      host: tableau-cluster.taxi.tst.yandex-team.ru
      port: 8060
      database: workgroup
      user: {{ TABLEAU['user'] }}
      password: {{ TABLEAU['password'] }}
      sslmode: disable
    tableau-taxi-api-oktell:
      host: tableau-cluster.taxi.tst.yandex-team.ru
      site:
      user: zomb-oktell-tgrm
      password: {{ TABLEAU_TAXI_API_OKTELL['password'] }}
usedesk:
  connection:
    taxi-dwh-usedesk-api:
      host: https://api.usedesk.ru/
      api_token: {{ TAXI_DWH_USEDESK_API['api_token'] }}
      app_id: {{ TAXI_DWH_USEDESK_API['app_id'] }}
telegram:
  connections:
    telegram_report_3421_bot:
      token: {{ TELEGRAM_REPORT_3421_BOT['token'] }}
telphin:
  connections:
    taxi-dwh-telphin-api:
      api_url: https://apiproxy.telphin.ru
      client_id: {{ TELPHIN_API_CHEF['client_id'] }}
      client_secret: {{ TELPHIN_API_CHEF['client_secret'] }}
      read_timeout: 30
riderlist:
  connections:
    default:
      host: '{{ RIDERLIST_CONNECTIONS_DEFAULT['host'] }}'
      headers:
        'X-Client-ID': "1"
        'X-API-Key': "{{ RIDERLIST_CONNECTIONS_DEFAULT['X-API-Key'] }}"
education:
  connections:
    eda_couriers:
      url: {{ EDUCATION_EDA_COURIERS['url'] }}
      client_id: {{ EDUCATION_EDA_COURIERS['client_id'] }}
      client_secret: {{ EDUCATION_EDA_COURIERS['client_secret'] }}
support_moderation:
  connections:
    default:
      token: {{ SUPPORT_MODERATION_CONNECTION['token'] }}
      host: support-moderation.taxi.yandex-team.ru
gizmo:
  connections:
    support:
      token: {{ TAXI_DWH_GIZMO['token'] }}
      token_secret: {{ TAXI_DWH_GIZMO['secret'] }}
tvm:
  services:
    taxi-dmp:
      id: "2019659"
      secret: "{{ TVM_TAXI_DMP_TVM_CLIENT_TEST['client_secret'] }}"
