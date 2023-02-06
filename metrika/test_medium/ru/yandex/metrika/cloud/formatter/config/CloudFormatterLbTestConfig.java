package ru.yandex.metrika.cloud.formatter.config;

import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.consumer.stream.StreamConsumerConfig;
import ru.yandex.kikimr.persqueue.producer.async.AsyncProducerConfig;
import ru.yandex.kikimr.persqueue.proxy.ProxyBalancer;
import ru.yandex.metrika.cloud.formatter.common.producers.LbProducerAsyncPool;
import ru.yandex.metrika.cloud.formatter.common.producers.LbProducerAsyncPoolBuilder;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.util.concurrent.Pools;


@Configuration
public class CloudFormatterLbTestConfig {


    public static final String TEST_CLOUD_VISITS_TOPIC = "/test/cloud-visits-log";
    public static final String TEST_FORMATTED_CLOUD_VISITS_TOPIC = "/test/formatted-cloud-visits-log";

    public static final String TEST_CONSUMER = "/test/consumer";
    public static final int TOPICS_PARTITIONS = 5;

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
    public AsyncProducerConfig baseProducerConfigForVisits() {
        return AsyncProducerConfig.builder(TEST_FORMATTED_CLOUD_VISITS_TOPIC, "default".getBytes())
                .build();
    }

    @Bean
    public ExecutorService consumerTestPool() {
        return Pools.newNamedFixedThreadPool(3, "consumer-test-pool");
    }

    @Bean
    public StreamConsumerConfig baseStreamConsumerConfigForVisits(ExecutorService consumerTestPool) {
        return StreamConsumerConfig.builder(List.of(TEST_CLOUD_VISITS_TOPIC), TEST_CONSUMER)
                .configureReader(builder -> builder
                        .setMaxUnconsumedReads(1)
                )
                .setExecutor(consumerTestPool)
                .configureCommiter(builder -> builder.setMaxUncommittedReads(1))
                .configureRetries(retries ->
                        retries.enable()
                                .setPolicy(10, TimeUnit.SECONDS)
                                .setShouldRestartOnUncaughtError(() -> true)
                                .setShouldRestartOnError((e) -> true)
                                .setShouldRetryOnConnect((e) -> true)
                                .setShouldRestartOnClose(() -> true)
                )
                .build();
    }

    @Bean
    public ExecutorService producerTestPool() {
        return Pools.newNamedFixedThreadPool(3, "producer-test-pool");
    }

    @Bean
    public LbProducerAsyncPool producerAsyncPool(
            LogbrokerClientAsyncFactory factory,
            AsyncProducerConfig baseProducerConfigForVisits,
            ExecutorService producerTestPool
    ) {
        return new LbProducerAsyncPoolBuilder().
                setFactory(factory)
                .setBaseConfig(baseProducerConfigForVisits)
                .setCacheExecutor(producerTestPool)
                .setSizeLimit(9000)
                .build();
    }
}
