<?xml version="1.0" encoding="UTF-8"?>
<yandex>
    <pushApiSettings>
        <daemonRoot>${daemonRoot}</daemonRoot>
        <apiUrl>http://localhost:${apiPort}</apiUrl>
    </pushApiSettings>

    <mysql_counters>
        <host>${RECIPE_MYSQL_HOST}</host>
        <port>${RECIPE_MYSQL_PORT}</port>
        <user>${RECIPE_MYSQL_USER}</user>
        <db>conv_main</db>
    </mysql_counters>
    <mysql_mobile_ro>
        <host>${RECIPE_MYSQL_HOST}</host>
        <port>${RECIPE_MYSQL_PORT}</port>
        <user>${RECIPE_MYSQL_USER}</user>
        <db>mobile</db>
    </mysql_mobile_ro>
    <mysql_mobile_rw>
        <host>${RECIPE_MYSQL_HOST}</host>
        <port>${RECIPE_MYSQL_PORT}</port>
        <user>${RECIPE_MYSQL_USER}</user>
        <db>mobile</db>
    </mysql_mobile_rw>
    <mysql_misc_mobile>
        <host>${RECIPE_MYSQL_HOST}</host>
        <port>${RECIPE_MYSQL_PORT}</port>
        <user>${RECIPE_MYSQL_USER}</user>
        <db>mobile</db>
    </mysql_misc_mobile>
    <mysql_mobile_rbac_ro>
        <host>${RECIPE_MYSQL_HOST}</host>
        <port>${RECIPE_MYSQL_PORT}</port>
        <user>${RECIPE_MYSQL_USER}</user>
        <db>rbac</db>
    </mysql_mobile_rbac_ro>
    <mysql_mobile_rbac_rw>
        <host>${RECIPE_MYSQL_HOST}</host>
        <port>${RECIPE_MYSQL_PORT}</port>
        <user>${RECIPE_MYSQL_USER}</user>
        <db>rbac</db>
    </mysql_mobile_rbac_rw>

    <mdsS3Properties>
        <endpoint>${mdsEndpoint}</endpoint>
        <appMetricaAccessKey>${mdsAccessKey}</appMetricaAccessKey>
        <appMetricaSecretKey>${mdsSecretKey}</appMetricaSecretKey>
        <pushLogBucket>appmetrica-push</pushLogBucket>
    </mdsS3Properties>

    <pushRestriction>
        <allowAppId index="1">185600</allowAppId>
    </pushRestriction>

    <authUtils>
        <useFio>false</useFio>
    </authUtils>

    <tvmSettings>
        <enabled>false</enabled>
    </tvmSettings>

    <requestStatInserter>
        <enabled>false</enabled>
    </requestStatInserter>

    <mysqlStatInserter>
        <enabled>false</enabled>
    </mysqlStatInserter>

    <clickhouseStatInserter>
        <enabled>false</enabled>
    </clickhouseStatInserter>

    <ydbTxStatInserter>
        <enabled>false</enabled>
    </ydbTxStatInserter>

    <ydbRequestStatInserter>
        <enabled>false</enabled>
    </ydbRequestStatInserter>

    <ydbMonitoringStatInserter>
        <enabled>false</enabled>
    </ydbMonitoringStatInserter>

    <ydbMobmetPushesProperties>
        <endpoint>${YDB_ENDPOINT}</endpoint>
        <database>${YDB_DATABASE}</database>
    </ydbMobmetPushesProperties>
</yandex>
