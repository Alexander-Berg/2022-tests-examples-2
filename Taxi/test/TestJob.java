package ru.yandex.taxi.dmp.flink.test;

import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.taxi.dmp.flink.config.Environment;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.LogbrokerConsumerConfig;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.LogbrokerConsumers;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.producer.LogbrokerProducerConfig;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.producer.LogbrokerProducers;
import ru.yandex.taxi.dmp.flink.utils.FlinkUtils;

@SuppressWarnings("checkstyle:HideUtilityClassConstructor")
public class TestJob {
    private static final transient Logger log = LoggerFactory.getLogger(TestJob.class);

    private static TestArgs parsedArgs;

    public static void main(String[] args) throws Exception {
        parsedArgs = new TestArgs(Environment.fromString(args[0]));

        StreamExecutionEnvironment env = FlinkUtils.defaultEnvironment(parsedArgs);

        var data = LogbrokerConsumers.readLbkxNoWatermarks(env,
                getLogbrokerConsumerConfig("/taxi/replication/testing/topics/groceries-offers"),
                String.class, (FlatMapFunction<String, String>) (value, out) -> out.collect(value));


        LogbrokerProducers.writeLb(
                data,
                LogbrokerProducerConfig
                        .builder("/logbroker-playground/sashbel/testing-grocery-offers")
                        .setDefaultTvmCredentials(),
                new SimpleStringSchema()
        );

        env.execute(parsedArgs.getServiceName());
    }

    private static LogbrokerConsumerConfig.Builder getLogbrokerConsumerConfig(String topic) {
        return LogbrokerConsumerConfig
                .builder(topic, parsedArgs.getLogbrokerConsumer())
                .setDefaultTvmCredentials();
    }
}
