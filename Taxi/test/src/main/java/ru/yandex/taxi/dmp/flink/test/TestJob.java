package ru.yandex.taxi.dmp.flink.test;

import java.util.Set;

import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.taxi.dmp.flink.config.Environment;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.Installations;
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

        var names = LogbrokerConsumers.readLbNoWatermarks(env,
                Set.of(Installations.LOGBROKER.SAS, Installations.LOGBROKER.VLA),
                getLogbrokerConsumerConfig(parsedArgs.getTestInTopic()),
                new SimpleStringSchema());

        var result = names.map(name -> "Hello, " + name).uid("map");

        LogbrokerProducers.writeLb(
                result,
                LogbrokerProducerConfig.builder(parsedArgs.getTestOutTopic()).setDefaultOAuthCredentials(),
                new SimpleStringSchema()
        );

        env.execute(parsedArgs.getServiceName());
    }

    private static LogbrokerConsumerConfig.Builder getLogbrokerConsumerConfig(String topic) {
        return LogbrokerConsumerConfig
                .builder(topic, parsedArgs.getLogbrokerConsumer())
                .setDefaultOAuthCredentials();
    }
}
