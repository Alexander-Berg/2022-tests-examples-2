<?xml version="1.0" encoding="UTF-8"?>
<yandex>
    <jmxServerConnector>
        <serviceUrl>service:jmx:jmxmp://localhost:${jmxPort}</serviceUrl>
    </jmxServerConnector>

    <dwarfProcessor>
        <symbolsCutterPath>${symbolsCutterPath}</symbolsCutterPath>
    </dwarfProcessor>

    <crashDecoderInputQueuesProperties>
        <rootPath>${inputQueuesRootPath}</rootPath>
    </crashDecoderInputQueuesProperties>

    <crashDecoderOutputQueuesProperties>
        <rootPath>${outputQueuesRootPath}</rootPath>
    </crashDecoderOutputQueuesProperties>

    <crashDecoderWriteTemplateProvider>
        <database>${outputDataBase}</database>
    </crashDecoderWriteTemplateProvider>

    <mysql_mobile>
        <host>${RECIPE_MYSQL_HOST}</host>
        <port>${RECIPE_MYSQL_PORT}</port>
        <user>${RECIPE_MYSQL_USER}</user>
        <db>mobile</db>
    </mysql_mobile>

    <zookeeperSettings>
        <node index="0">
            <host>${RECIPE_ZOOKEEPER_HOST}</host>
            <port>${RECIPE_ZOOKEEPER_PORT}</port>
        </node>
    </zookeeperSettings>

    <calcCloudSettings>
        <name>dev_cloud</name>
        <zookeeper_path>/calc_cloud_development</zookeeper_path>
        <replication_factor>1</replication_factor>
        <datacenters>
            <datacenter index="1">
                <clickhouses>
                    <node index="1">
                        <host>${RECIPE_CLICKHOUSE_HOST}</host>
                        <port>${RECIPE_CLICKHOUSE_NATIVE_PORT}</port>
                        <http_port>${RECIPE_CLICKHOUSE_HTTP_PORT}</http_port>
                    </node>
                </clickhouses>
            </datacenter>
        </datacenters>
    </calcCloudSettings>
    <crashDecoderServerSelector>
        <replicationFactor>1</replicationFactor>
    </crashDecoderServerSelector>

    <mobileCrashesPgProps>
        <host index="0">${POSTGRES_RECIPE_HOST}</host>
        <port>${POSTGRES_RECIPE_PORT}</port>
        <user>${POSTGRES_RECIPE_USER}</user>
        <db>${POSTGRES_RECIPE_DBNAME}</db>
        <pool>true</pool>
    </mobileCrashesPgProps>

    <ydbMobmetCrashesProperties>
        <endpoint>${YDB_ENDPOINT}</endpoint>
        <database>${YDB_DATABASE}</database>
    </ydbMobmetCrashesProperties>

    <mobileCrashesPoolingDataSource>
        <ssl>false</ssl>
    </mobileCrashesPoolingDataSource>

    <crashDecoderOutputQueueSelector>
        <layers>1</layers>
    </crashDecoderOutputQueueSelector>

    <demangler>
        <itaniumDemanglerPath>${itaniumDemangler}</itaniumDemanglerPath>
        <swiftDemanglerPath>${swiftDemangler}</swiftDemanglerPath>
    </demangler>

    <jugglerReporter>
        <enabled>false</enabled>
    </jugglerReporter>
</yandex>
