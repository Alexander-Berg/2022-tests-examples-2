package ru.yandex.metrika.cdp.api.tests.medium.service.dataservice;

import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.consumer.SyncConsumer;
import ru.yandex.kikimr.persqueue.consumer.sync.SyncConsumerConfig;
import ru.yandex.metrika.cdp.dto.core.ClientUpdate;
import ru.yandex.metrika.cdp.dto.core.OrderUpdate;
import ru.yandex.metrika.cdp.proto.ClientUpdateProtoSerializer;
import ru.yandex.metrika.cdp.proto.OrderUpdateProtoSerializer;
import ru.yandex.metrika.lb.serialization.Serializer;
import ru.yandex.metrika.lb.write.LogbrokerWriterConfig;
import ru.yandex.metrika.lb.write.LogbrokerWriterFactory;
import ru.yandex.metrika.lb.write.ReinitializingLogbrokerWriter;

@Configuration
public class LogbrokerConfigForDataService {

    @Bean(name = "clientsDownstreamConfig")
    public LogbrokerWriterConfig clientsDownstreamConfig() {
        var config = new LogbrokerWriterConfig();
        config.setTopic("/metrika/cdp/cdp-clients-topic");
        config.setSourceIdPrefix("cdp-experimental-writer");
        return config;
    }

    @Bean(name = "ordersDownstreamConfig")
    public LogbrokerWriterConfig ordersDownstreamConfig() {
        var config = new LogbrokerWriterConfig();
        config.setTopic("/metrika/cdp/cdp-orders-topic");
        config.setSourceIdPrefix("cdp-experimental-writer");
        return config;
    }

    @Bean
    public ClientUpdateProtoSerializer clientUpdateProtoSerializer() {
        return new ClientUpdateProtoSerializer();
    }

    @Bean
    public OrderUpdateProtoSerializer orderUpdateProtoSerializer() {
        return new OrderUpdateProtoSerializer();
    }

    @Bean
    public ReinitializingLogbrokerWriter<ClientUpdate> clientsDownstream(
            LogbrokerWriterFactory logbrokerWriterFactory,
            Serializer<ClientUpdate> clientSerializer,
            @Qualifier("clientsDownstreamConfig") LogbrokerWriterConfig clientsDownstreamConfig) {
        return logbrokerWriterFactory.reinitializingLogbrokerWriter(
                clientsDownstreamConfig,
                clientSerializer);
    }

    @Bean
    public ReinitializingLogbrokerWriter<OrderUpdate> ordersDownstream(
            LogbrokerWriterFactory logbrokerWriterFactory,
            Serializer<OrderUpdate> orderSerializer,
            @Qualifier("ordersDownstreamConfig") LogbrokerWriterConfig ordersDownstreamConfig) {
        return logbrokerWriterFactory.reinitializingLogbrokerWriter(
                ordersDownstreamConfig,
                orderSerializer
        );
    }

    @Bean("ordersSyncConsumerConfig")
    public SyncConsumerConfig ordersSyncConsumerConfig(@Qualifier("ordersDownstreamConfig") LogbrokerWriterConfig ordersDownstreamConfig) {
        return SyncConsumerConfig
                .builder(List.of(ordersDownstreamConfig.getTopic()),
                        ordersDownstreamConfig.getSourceIdPrefix())
                .setReadDataTimeout(3, TimeUnit.SECONDS)
                .configureReader(x -> x.setMaxCount(0))
                .build();
    }

    @Bean("ordersSyncConsumer")
    public SyncConsumer ordersSyncConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory,
                                           @Qualifier("ordersSyncConsumerConfig") SyncConsumerConfig ordersSyncConsumerConfig)
            throws ExecutionException, InterruptedException, TimeoutException {
        var syncConsumer = logbrokerClientAsyncFactory.syncConsumer(ordersSyncConsumerConfig).get();
        syncConsumer.init();
        return syncConsumer;
    }

    @Bean("contactsSyncConsumerConfig")
    public SyncConsumerConfig contactsSyncConsumerConfig(@Qualifier("clientsDownstreamConfig") LogbrokerWriterConfig clientsDownstreamConfig) {
        return SyncConsumerConfig
                .builder(List.of(clientsDownstreamConfig.getTopic()),
                        clientsDownstreamConfig.getSourceIdPrefix())
                .setReadDataTimeout(3, TimeUnit.SECONDS)
                .configureReader(x -> x.setMaxCount(0))
                .build();
    }

    @Bean("contactsSyncConsumer")
    public SyncConsumer contactsSyncConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory,
                                             @Qualifier("contactsSyncConsumerConfig") SyncConsumerConfig contactsSyncConsumerConfig)
            throws ExecutionException, InterruptedException, TimeoutException {
        var syncConsumer = logbrokerClientAsyncFactory.syncConsumer(contactsSyncConsumerConfig).get();
        syncConsumer.init();
        return syncConsumer;
    }
}
