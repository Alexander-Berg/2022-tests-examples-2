package ru.yandex.metrika.cdp.core.spring;


import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.consumer.SyncConsumer;
import ru.yandex.kikimr.persqueue.consumer.sync.SyncConsumerConfig;
import ru.yandex.metrika.cdp.config.LogbrokerConfig;
import ru.yandex.metrika.cdp.core.processing.ClientUpdatesProcessor;
import ru.yandex.metrika.cdp.core.processing.OrderUpdatesProcessor;
import ru.yandex.metrika.cdp.dto.core.ClientUpdate;
import ru.yandex.metrika.cdp.dto.core.OrderUpdate;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStatRegistrator;
import ru.yandex.metrika.lb.serialization.Serializer;
import ru.yandex.metrika.lb.waitable.WaitingLogbrokerConfig;
import ru.yandex.metrika.lb.waitable.WaitingLogbrokerWriter;
import ru.yandex.metrika.lb.write.LogbrokerWriter;
import ru.yandex.metrika.lb.write.LogbrokerWriterConfig;
import ru.yandex.metrika.lb.write.LogbrokerWriterFactory;

@Configuration
@Import({
        CdpCoreConfig.class,
        LogbrokerConfig.class,
        WaitingLogbrokerConfig.class
})
public class CdpCoreTestConfig {
    private String clientKeyTopic;
    private String orderKeyTopic;
    private String changedEmailsAndPhonesTopic;
    private String cdpClientIdChangesTopic;
    private String clientKeyConsumerPath;
    private String orderKeyConsumerPath;
    private String changedEmailsAndPhonesConsumerPath;
    private String cdpClientIdChangesConsumerPath;


    @Bean
    public LogbrokerWriterConfig orderUpdatesLogbrokerWriterConfig() {
        var config = new LogbrokerWriterConfig();
        config.setTopic("cdp-orders-topic");
        return config;
    }

    @Bean
    public LogbrokerWriter<OrderUpdate> orderUpdatesLogbrokerWriter(LogbrokerWriterFactory factory,
                                                                    Serializer<OrderUpdate> serializer,
                                                                    @Qualifier("orderUpdatesLogbrokerWriterConfig") LogbrokerWriterConfig orderUpdatesDownstreamConfig) {

        return factory.reinitializingLogbrokerWriter(
                orderUpdatesDownstreamConfig,
                serializer
        );
    }

    @Bean
    public WaitingLogbrokerWriter<OrderUpdate> waitingOrderUpdatesWriter(LogbrokerWriter<OrderUpdate> delegate, OrderUpdatesProcessor processor, ProcessedMessagesStatRegistrator processedMessagesStatRegistrator) {
        return new WaitingLogbrokerWriter<>(delegate, processor, processedMessagesStatRegistrator);
    }

    @Bean
    public LogbrokerWriterConfig clientUpdatesLogbrokerWriterConfig() {
        var config = new LogbrokerWriterConfig();
        config.setTopic("cdp-clients-topic");
        return config;
    }

    @Bean
    public LogbrokerWriter<ClientUpdate> clientUpdatesLogbrokerWriter(LogbrokerWriterFactory factory,
                                                                      Serializer<ClientUpdate> serializer,
                                                                      @Qualifier("clientUpdatesLogbrokerWriterConfig") LogbrokerWriterConfig clientUpdatesDownstreamConfig) {
        return factory.reinitializingLogbrokerWriter(
                clientUpdatesDownstreamConfig,
                serializer
        );
    }

    @Bean
    public WaitingLogbrokerWriter<ClientUpdate> waitingClientUpdatesWriter(LogbrokerWriter<ClientUpdate> delegate, ClientUpdatesProcessor processor, ProcessedMessagesStatRegistrator processedMessagesStatRegistrator) {
        return new WaitingLogbrokerWriter<>(delegate, processor, processedMessagesStatRegistrator);
    }

    @Bean
    public SyncConsumerConfig ordersKeySyncConsumerConfig() {
        return SyncConsumerConfig
                .builder(List.of(orderKeyTopic), orderKeyConsumerPath)
                .setReadDataTimeout(3, TimeUnit.SECONDS)
                .configureReader(x -> x.setMaxCount(0))
                .build();
    }

    @Bean
    public SyncConsumer orderUpdatesSyncConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory,
                                                 @Qualifier("ordersKeySyncConsumerConfig") SyncConsumerConfig orderKeysSyncConsumerConfig)
            throws ExecutionException, InterruptedException, TimeoutException {
        var syncConsumer = logbrokerClientAsyncFactory.syncConsumer(orderKeysSyncConsumerConfig).get();
        syncConsumer.init();
        return syncConsumer;
    }

    @Bean
    public SyncConsumerConfig clientsKeysSyncConsumerConfig() {
        return SyncConsumerConfig
                .builder(List.of(clientKeyTopic), clientKeyConsumerPath)
                .setReadDataTimeout(3, TimeUnit.SECONDS)
                .configureReader(x -> x.setMaxCount(0))
                .build();
    }

    @Bean
    public SyncConsumer clientUpdatesSyncConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory, @Qualifier("clientsKeysSyncConsumerConfig") SyncConsumerConfig config)
            throws ExecutionException, InterruptedException, TimeoutException {
        var syncConsumer = logbrokerClientAsyncFactory.syncConsumer(config).get();
        syncConsumer.init();
        return syncConsumer;
    }

    @Bean
    public SyncConsumerConfig cdpClientIdChangesConsumerConfig() {
        return SyncConsumerConfig
                .builder(List.of(cdpClientIdChangesTopic), cdpClientIdChangesConsumerPath)
                .setReadDataTimeout(3, TimeUnit.SECONDS)
                .configureReader(x -> x.setMaxCount(0))
                .build();
    }

    @Bean
    public SyncConsumer cdpClientIdChangesConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory,
                                                   @Qualifier("cdpClientIdChangesConsumerConfig") SyncConsumerConfig config)
            throws InterruptedException, TimeoutException, ExecutionException {
        var syncConsumer = logbrokerClientAsyncFactory.syncConsumer(config).get();
        syncConsumer.init();
        return syncConsumer;
    }

    @Bean
    public SyncConsumerConfig changedEmailsAndPhonesConsumerConfig() {
        return SyncConsumerConfig
                .builder(List.of(changedEmailsAndPhonesTopic), changedEmailsAndPhonesConsumerPath)
                .setReadDataTimeout(3, TimeUnit.SECONDS)
                .configureReader(x -> x.setMaxCount(0))
                .build();
    }

    @Bean
    public SyncConsumer changedEmailsAndPhonesConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory,
                                                       @Qualifier("changedEmailsAndPhonesConsumerConfig") SyncConsumerConfig config)
            throws InterruptedException, TimeoutException, ExecutionException {
        var syncConsumer = logbrokerClientAsyncFactory.syncConsumer(config).get();
        syncConsumer.init();
        return syncConsumer;
    }

    public void setClientKeyTopic(String clientKeyTopic) {
        this.clientKeyTopic = clientKeyTopic;
    }

    public void setClientKeyConsumerPath(String clientKeyConsumerPath) {
        this.clientKeyConsumerPath = clientKeyConsumerPath;
    }

    public void setOrderKeyTopic(String orderKeyTopic) {
        this.orderKeyTopic = orderKeyTopic;
    }

    public void setOrderKeyConsumerPath(String orderKeyConsumerPath) {
        this.orderKeyConsumerPath = orderKeyConsumerPath;
    }

    public void setChangedEmailsAndPhonesTopic(String changedEmailsAndPhonesTopic) {
        this.changedEmailsAndPhonesTopic = changedEmailsAndPhonesTopic;
    }

    public void setCdpClientIdChangesTopic(String cdpClientIdChangesTopic) {
        this.cdpClientIdChangesTopic = cdpClientIdChangesTopic;
    }

    public void setChangedEmailsAndPhonesConsumerPath(String changedEmailsAndPhonesConsumerPath) {
        this.changedEmailsAndPhonesConsumerPath = changedEmailsAndPhonesConsumerPath;
    }

    public void setCdpClientIdChangesConsumerPath(String cdpClientIdChangesConsumerPath) {
        this.cdpClientIdChangesConsumerPath = cdpClientIdChangesConsumerPath;
    }
}
