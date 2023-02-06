<?xml version="1.0" encoding="UTF-8"?>
<yandex>
    <cluster>
        <jmxServerConnector>
            <serviceUrl>service:jmx:jmxmp://localhost:${jmxPort}</serviceUrl>
        </jmxServerConnector>

        <visitsConsumerConfig>
            <topicPath>/webvisorlog</topicPath>
            <consumerPath>/consumer</consumerPath>
            <poolCoreSize>1</poolCoreSize>
        </visitsConsumerConfig>

        <lbWriterEventsConfig>
            <topic>${logbrokerEventsTopic}</topic>
            <partitionsCount>1</partitionsCount>
            <compressionCodec>RAW</compressionCodec>
        </lbWriterEventsConfig>

        <lbWriterStaticUrlsConfig>
            <topic>${logbrokerStaticTopic}</topic>
            <partitionsCount>1</partitionsCount>
            <compressionCodec>RAW</compressionCodec>
        </lbWriterStaticUrlsConfig>

        <lbWriterCryptaConfig>
            <topic>${logbrokerCryptaTopic}</topic>
            <partitionsCount>1</partitionsCount>
            <compressionCodec>RAW</compressionCodec>
        </lbWriterCryptaConfig>

        <lbWriterScrollsConfig>
            <topic>${logbrokerScrollsTopic}</topic>
            <partitionsCount>1</partitionsCount>
            <compressionCodec>RAW</compressionCodec>
        </lbWriterScrollsConfig>

        <lbWriterFormsConfig>
            <topic>${logbrokerFormsTopic}</topic>
            <partitionsCount>1</partitionsCount>
            <compressionCodec>RAW</compressionCodec>
        </lbWriterFormsConfig>

        <webvisorYtProperties>
            <rootYTPath>${ytPathPrefix}</rootYTPath>
            <proxies index="0">${YT_PROXY}</proxies>
        </webvisorYtProperties>

        <webvisorYtRpcProperties>
            <rootYTPath>${ytPathPrefix}</rootYTPath>
            <proxies index="0">${YT_PROXY}</proxies>
        </webvisorYtRpcProperties>

        <countersServerClient>
            <replicas index="1">
                <host>${targetHost}</host>
                <port>${RECIPE_COUNTERS_SERVER_PORT}</port>
            </replicas>
        </countersServerClient>

        <lbProxyParamsHolder>
            <host>${targetHost}</host>
            <proxyPort>${LOGBROKER_PORT}</proxyPort>
            <balancerPort>${LOGBROKER_PORT}</balancerPort>
        </lbProxyParamsHolder>

        <zookeeperSettings>
            <node index="1">
                <host>${RECIPE_ZOOKEEPER_HOST}</host>
                <port>${RECIPE_ZOOKEEPER_PORT}</port>
            </node>
        </zookeeperSettings>

        <statLogHosts>
            <sources index="0">
                <host>${RECIPE_CLICKHOUSE_HOST}</host>
                <port>${RECIPE_CLICKHOUSE_HTTP_PORT}</port>
                <db>stats</db>
            </sources>
        </statLogHosts>

        <wvFormsScrollsConnectionProperties>
            <ssl>false</ssl>
        </wvFormsScrollsConnectionProperties>
        <event2TableManager>
            <numberOfShards>2</numberOfShards>
        </event2TableManager>
        <layerToShardMapper>
            <element index="0">
                <layer>1</layer>
                <shard>1</shard>
            </element>
            <element index="1">
                <layer>2</layer>
                <shard>1</shard>
            </element>
            <element index="3">
                <layer>3</layer>
                <shard>1</shard>
            </element>
        </layerToShardMapper>
        <countersLogger>
            <enabled>false</enabled>
        </countersLogger>
        <visor3dProperties>
            <chunkMaxCompressionVersion>0</chunkMaxCompressionVersion>
            <eventMaxCompressionVersion>0</eventMaxCompressionVersion>
            <pageMaxCompressionVersion>0</pageMaxCompressionVersion>
            <mutationMaxCompressionVersion>0</mutationMaxCompressionVersion>
        </visor3dProperties>

        <webvisorYtCopyToSasProperties>
            <rootYTPath>${ytPathPrefix}</rootYTPath>
            <proxies index="0">${YT_PROXY}</proxies>
        </webvisorYtCopyToSasProperties>
        <webvisorYtCopyToVlaProperties>
            <rootYTPath>${ytPathPrefix}</rootYTPath>
            <proxies index="0">${YT_PROXY}</proxies>
        </webvisorYtCopyToVlaProperties>

        <appenderConsumerToSasConfig>
            <topicPath>wv-append-to-sas-log</topicPath>
            <consumerPath>/consumer</consumerPath>
        </appenderConsumerToSasConfig>
        <appenderConsumerToVlaConfig>
            <topicPath>wv-append-to-vla-log</topicPath>
            <consumerPath>/consumer</consumerPath>
        </appenderConsumerToVlaConfig>

        <lbWriterAppendVlaConfig>
            <partitionsCount>1</partitionsCount>
            <compressionCodec>RAW</compressionCodec>
            <topic>wv-append-to-vla-log</topic>
        </lbWriterAppendVlaConfig>
        <lbWriterAppendSasConfig>
            <partitionsCount>1</partitionsCount>
            <compressionCodec>RAW</compressionCodec>
            <topic>wv-append-to-sas-log</topic>
        </lbWriterAppendSasConfig>
    </cluster>
</yandex>
