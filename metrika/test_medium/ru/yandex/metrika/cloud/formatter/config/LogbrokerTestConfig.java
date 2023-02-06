package ru.yandex.metrika.cloud.formatter.config;

import java.nio.ByteBuffer;

import javax.annotation.Nonnull;

import org.springframework.context.annotation.Bean;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.proxy.ProxyBalancer;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.lb.ClientAsyncFactory;
import ru.yandex.metrika.lb.read.AbstractLogbrokerConsumerConfig;
import ru.yandex.metrika.lb.read.GeneralLogbrokerConsumerConfig;
import ru.yandex.metrika.lb.read.LogbrokerConsumerFactory;
import ru.yandex.metrika.lb.serialization.BatchSerializer;
import ru.yandex.metrika.lb.serialization.proto.ProtoSerializer;
import ru.yandex.metrika.lb.serialization.protoseq.ProtoSeqBatchSerializer;

public class LogbrokerTestConfig {

    public static final String POOL_TOPIC = "/test/pool-topic";

    @Bean
    public LogbrokerClientAsyncFactory logbrokerClientFactory() {
        return new LogbrokerClientAsyncFactory(
                new ProxyBalancer(
                        EnvironmentHelper.logbrokerHost,
                        EnvironmentHelper.logbrokerPort,
                        EnvironmentHelper.logbrokerPort
                )
        );
    }

    @Bean
    public ClientAsyncFactory clientAsyncFactory(LogbrokerClientAsyncFactory logbrokerClientFactory) {
        return ClientAsyncFactory.fromDefaultFactory(logbrokerClientFactory);
    }

    @Bean
    public LogbrokerConsumerFactory consumerFactory(ClientAsyncFactory clientAsyncFactory) {
        return new LogbrokerConsumerFactory(clientAsyncFactory);
    }

    private AbstractLogbrokerConsumerConfig createDefaultTestConfig() {
        var config = new GeneralLogbrokerConsumerConfig();

        config.setPoolName("test-result-reader");
        config.setPoolMaxCoreSize(4);

        return config;
    }

    @Bean
    public AbstractLogbrokerConsumerConfig poolConsumerConfig() {
        var config = createDefaultTestConfig();

        config.setTopicPath(POOL_TOPIC);
        config.setConsumerPath("/test/consumer");

        return config;
    }

    @Bean
    public BatchSerializer<Integer> intSerializer() {
        return new ProtoSeqBatchSerializer<>(new ProtoSerializer<>() {

            @Nonnull
            @Override
            public Integer deserialize(ByteBuffer byteBuffer) {
                return byteBuffer.getInt();
            }

            @Override
            public byte[] serialize(Integer i) {
                return ByteBuffer.allocate(4).putInt(i).array();
            }
        });
    }

}
