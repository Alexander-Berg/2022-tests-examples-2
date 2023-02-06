package ru.yandex.metrika.cloud.formatter.common.producer;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import com.google.common.util.concurrent.AtomicLongMap;
import org.junit.After;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.producer.AsyncProducer;
import ru.yandex.kikimr.persqueue.producer.async.AsyncProducerConfig;
import ru.yandex.metrika.cloud.formatter.common.producers.LbProducerAsyncPoolBuilder;
import ru.yandex.metrika.cloud.formatter.common.producers.ProducerAddress;
import ru.yandex.metrika.cloud.formatter.config.LogbrokerTestConfig;
import ru.yandex.metrika.lb.read.AbstractLogbrokerConsumerConfig;
import ru.yandex.metrika.lb.read.LogbrokerConsumerFactory;
import ru.yandex.metrika.lb.read.SelfListeningStreamConsumer;
import ru.yandex.metrika.lb.read.processing.LogbrokerMessageProcessor;
import ru.yandex.metrika.lb.read.processing.LogbrokerSimpleProcessor;
import ru.yandex.metrika.lb.read.processing.ProcessingStreamListener;
import ru.yandex.metrika.lb.serialization.BatchSerializer;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.collections.Try;
import ru.yandex.metrika.util.concurrent.Pools;

import static java.lang.Thread.sleep;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.hamcrest.core.Every.everyItem;
import static org.hamcrest.core.IsEqual.equalTo;
import static org.mockito.ArgumentMatchers.any;
import static ru.yandex.metrika.cloud.formatter.config.LogbrokerTestConfig.POOL_TOPIC;

@RunWith(SpringRunner.class)
@ContextConfiguration(classes = {LbProducerAsyncPoolImplTest.TestConfig.class})
public class LbProducerAsyncPoolImplTest {
    @Autowired
    LogbrokerClientAsyncFactory factory;

    @Autowired
    AsyncProducerConfig baseWriterConfig;

    @Autowired
    ThreadPoolExecutor threadPoolExecutor;

    @Autowired
    BatchSerializer<Integer> serializer;

    @Autowired
    SelfListeningStreamConsumer resultConsumer;

    @Autowired
    AtomicLongMap<Integer> result;

    @After
    public void dropResult() {
        result.clear();
    }

    @Test
    public void getAndWriteStress() throws InterruptedException {
        final int totalSize = 1000;

        ArrayList<Integer> data = Stream.iterate(0, n -> n + 1)
                .limit(totalSize)
                .collect(Collectors.toCollection(ArrayList::new));

        var pool = new LbProducerAsyncPoolBuilder()
                .setFactory(factory)
                .setBaseConfig(baseWriterConfig)
                .setCacheExecutor(threadPoolExecutor)
                .setSizeLimit(5)
                .build();

        F.sequence(
                F.map(data, i ->
                        pool.getAsync(new ProducerAddress("" + getOwnerId(i), i % 2))
                                .thenCompose(producer -> producer.write(serializer.serialize(List.of(i))))
                )
        ).join();


        resultConsumer.startConsume();

        while (result.size() < totalSize) {
            sleep(1000);
            System.out.println("waiting... " + result.size() + "/" + totalSize);
        }

        Assert.assertThat(result.asMap().keySet(), containsInAnyOrder(data.toArray()));
        Assert.assertThat(result.asMap().values(), everyItem(equalTo(1L)));
    }

    @Test
    public void stressWithBrokenWriters() throws InterruptedException {
        final int totalSize = 1000;

        AtomicInteger brokenNumber = new AtomicInteger(0);
        ArrayList<Integer> data = Stream.iterate(0, n -> n + 1)
                .limit(totalSize)
                .collect(Collectors.toCollection(ArrayList::new));

        LogbrokerClientAsyncFactory brokenFactory = Mockito.spy(factory);
        Mockito.doAnswer(invocation -> {
            var futureProducer = (CompletableFuture<AsyncProducer>) invocation.callRealMethod();
            if (brokenNumber.incrementAndGet() < totalSize) {
                return futureProducer.thenApply(workingProducer -> {
                    var totallyBrokenProducer = Mockito.spy(workingProducer);
                    Mockito.doReturn(CompletableFuture.failedStage(new RuntimeException("Broken producer kek")))
                            .when(totallyBrokenProducer).write(any());
                    return totallyBrokenProducer;
                });
            }
            return futureProducer;
        }).when(brokenFactory).asyncProducer(any(AsyncProducerConfig.class));

        var pool = new LbProducerAsyncPoolBuilder()
                .setFactory(brokenFactory)
                .setBaseConfig(baseWriterConfig)
                .setCacheExecutor(threadPoolExecutor)
                .setSizeLimit(20)
                .build();

        F.sequence(
                F.map(data, i ->
                        Try.retryAsync(() -> pool.runWithInvalidationOnFail(new ProducerAddress("" + getOwnerId(i)),
                                        producer -> producer.write(serializer.serialize(List.of(i)))),
                                totalSize + 1, 20)
                )
        ).join();


        resultConsumer.startConsume();

        while (result.size() < totalSize) {
            sleep(1000);
            System.out.println("waiting... " + result.size() + "/" + totalSize);
        }

        Assert.assertThat(result.asMap().keySet(), containsInAnyOrder(data.toArray()));
        Assert.assertThat(result.asMap().values(), everyItem(equalTo(1L)));
    }

    @Test
    public void stressWithFlappingWriters() throws InterruptedException {
        final int totalSize = 1000;

        AtomicInteger brokenNumber = new AtomicInteger(0);
        ArrayList<Integer> data = Stream.iterate(0, n -> n + 1)
                .limit(totalSize)
                .collect(Collectors.toCollection(ArrayList::new));

        LogbrokerClientAsyncFactory brokenFactory = Mockito.spy(factory);
        Mockito.doAnswer(invocation -> {
            var futureProducer = (CompletableFuture<AsyncProducer>) invocation.callRealMethod();
            return futureProducer.thenApply(workingProducer -> {
                var totallyBrokenProducer = Mockito.spy(workingProducer);
                Mockito.doAnswer(producerInvocation -> {
                            if (brokenNumber.incrementAndGet() < totalSize) {
                                return CompletableFuture.failedStage(new RuntimeException("Failed write kek"));
                            } else {
                                return producerInvocation.callRealMethod();
                            }
                        })
                        .when(totallyBrokenProducer).write(any());
                return totallyBrokenProducer;
            });
        }).when(brokenFactory).asyncProducer(any(AsyncProducerConfig.class));

        var pool = new LbProducerAsyncPoolBuilder()
                .setFactory(brokenFactory)
                .setBaseConfig(baseWriterConfig)
                .setCacheExecutor(threadPoolExecutor)
                .setSizeLimit(20)
                .build();

        F.sequence(
                F.map(data, i ->
                        pool.runWithInvalidationOnFail(
                                new ProducerAddress("" + getOwnerId(i)),
                                producer -> Try.retryAsync(() -> producer.write(serializer.serialize(List.of(i))),
                                        totalSize + 1, 20)
                        )
                )
        ).join();


        resultConsumer.startConsume();

        while (result.size() < totalSize) {
            sleep(1000);
            System.out.println("waiting... " + result.size() + "/" + totalSize);
        }

        Assert.assertThat(result.asMap().keySet(), containsInAnyOrder(data.toArray()));
        Assert.assertThat(result.asMap().values(), everyItem(equalTo(1L)));
    }


    static int getOwnerId(int i) {
        return i % 10;
    }

    @Configuration
    @Import(LogbrokerTestConfig.class)
    public static class TestConfig {
        @Bean
        ThreadPoolExecutor threadPoolExecutor() {
            return Pools.newNamedFixedThreadPool(10, "my-local-pool");
        }

        @Bean
        AsyncProducerConfig baseWriterConfig() {
            return AsyncProducerConfig
                    .builder(POOL_TOPIC, "default".getBytes())
                    .build();
        }

        @Bean
        AtomicLongMap<Integer> resultCollection() {
            return AtomicLongMap.create();
        }

        @Bean
        LogbrokerSimpleProcessor<Integer> resultCollector(AtomicLongMap<Integer> resultCollection) {
            return messages -> {
                messages.forEach(resultCollection::incrementAndGet);
                return CompletableFuture.allOf();
            };
        }

        @Bean
        public SelfListeningStreamConsumer resultConsumer(
                LogbrokerConsumerFactory consumerFactory,
                AbstractLogbrokerConsumerConfig poolConsumerConfig,
                LogbrokerMessageProcessor<Integer> resultCollector,
                BatchSerializer<Integer> intSerializer
        ) {
            return consumerFactory.processingConsumer(
                    poolConsumerConfig,
                    ProcessingStreamListener.withProcessor(resultCollector)
                            .withBatchSerializer(intSerializer)
                            .withoutSorting()
            );
        }

    }
}
