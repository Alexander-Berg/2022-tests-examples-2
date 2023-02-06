package ru.yandex.metrika.schedulerd.cron.task.monitoringd.v2;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Random;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import io.qameta.allure.Step;

import ru.yandex.kikimr.persqueue.LogbrokerClientFactory;
import ru.yandex.kikimr.persqueue.consumer.SyncConsumer;
import ru.yandex.kikimr.persqueue.consumer.sync.SyncConsumerConfig;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerReadResponse;
import ru.yandex.kikimr.persqueue.producer.AsyncProducer;
import ru.yandex.metrika.schedulerd.cron.task.monitoringd.LogbrokerSubscriber;

public class MonitoringLbSteps {
    private static final Random random = new Random();
    private final String topic;
    private final String consumer;
    private final long now;
    private final LogbrokerClientFactory factory;
    private SyncConsumer syncConsumer;
    private LogbrokerSubscriber subscriber;

    public MonitoringLbSteps(String topic, String consumer, long now, LogbrokerClientFactory factory) {
        this.topic = topic;
        this.consumer = consumer;
        this.now = now;
        this.factory = factory;
        this.syncConsumer = null;
        this.subscriber = null;
    }

    @Step("Создание натсроек подключения к LB")
    public static SyncConsumerConfig createLbConsumerConfig(String topic, String consumer) {
        return SyncConsumerConfig
                .builder(Set.of(topic), consumer)
                .setReadDataTimeout(10, TimeUnit.SECONDS)
                .setInitTimeout(10, TimeUnit.SECONDS)
                .setCommitTimeout(10, TimeUnit.SECONDS)
                .setReadBufferSize(100 * 1024 * 1024)
                .configureReader(readerConfigBuilder -> readerConfigBuilder
                        .setPartitionsAtOnce(5)
                        .setMaxInflightReads(1000)
                        .setMaxSize(1000)
                        .setMaxCount(1000)
                        .setMaxUnconsumedReads(1000)
                )
                .build();
    }

    @Step("Создание Consumer к LB")
    public static SyncConsumer createLbConsumer(LogbrokerClientFactory factory, SyncConsumerConfig config) throws InterruptedException {
        return factory.syncConsumer(config);
    }

    @Step("Очистка данных в LB перед записью тестовых данных")
    public static void cleanLbConsumer(SyncConsumer consumer) throws InterruptedException {
        try {
            // Очистка данных в очереди логброкера
            consumer.init();
            while (true) {
                ConsumerReadResponse response = consumer.read();
                if (response == null) {
                    consumer.close();
                    return;
                }
                consumer.commit(response.getCookie());
            }
        } catch (Exception ignore) {
            consumer.close();
        }
    }

    @Step("Задливка тестовых данных в LB")
    public static void prepareLbData(LogbrokerClientFactory factory, String topic, String consumer, List<byte[]> records) throws InterruptedException {
        AsyncProducer producer = factory.asyncProducer(topic, consumer.getBytes());
        producer.init().join();
        records.forEach(producer::write);
        producer.close();
    }

    @Step("Инициализация работы с LB")
    public void init(List<byte[]> lbData) throws Exception {
        if (lbData.isEmpty()) {
            return;
        }
        this.syncConsumer = initLb(lbData);
        this.subscriber = new SubscriberMock(syncConsumer);
    }

    public void cleanLbConsumer() throws InterruptedException {
        if (this.syncConsumer != null) {
            cleanLbConsumer(this.syncConsumer);
        }
    }

    public LogbrokerSubscriber getSubscriber() {
        return subscriber;
    }

    public SyncConsumer getSyncConsumer() {
        return syncConsumer;
    }

    @Step("Подготовка LB для тестов")
    public SyncConsumer initLb(List<byte[]> data) throws Exception {
        if (data.isEmpty()) {
            return null;
        }
        SyncConsumerConfig config = createLbConsumerConfig(topic, consumer);
        SyncConsumer consumer = createLbConsumer(this.factory, config);
        cleanLbConsumer(consumer);
        prepareLbData(factory, topic, this.consumer, data);
        consumer = createLbConsumer(this.factory, config);
        consumer.init();
        return consumer;
    }

    public byte[] lbStatus(String url, boolean isOk, int t) {
        return String.format("{" +
                        "\"sources\":[\"metrika\"]," +
                        "\"updated\":%s," +
                        "\"old\":%s," +
                        "\"new\":%s," +
                        "\"http_status\":%s," +
                        "\"url\":\"%s\"," +
                        "\"zora_http_status\":%s," +
                        "\"staging\":%s" +
                        "}",
                TimeUnit.MILLISECONDS.toSeconds(
                        now - TimeUnit.MINUTES.toMillis(t)
                ),
                isOk ? 4 : 0,
                isOk ? 0 : 3,
                isOk ? 200 : 500,
                url,
                200,
                0
        ).getBytes(StandardCharsets.UTF_8);
    }

    class SubscriberMock extends LogbrokerSubscriber {

        private final SyncConsumer consumer;

        public SubscriberMock(SyncConsumer consumer) {
            super(null, null, null);
            this.consumer = consumer;
        }

        @Override
        public SyncConsumer createSyncConsumer() throws TimeoutException, InterruptedException {
            return this.consumer;
        }
    }
}
