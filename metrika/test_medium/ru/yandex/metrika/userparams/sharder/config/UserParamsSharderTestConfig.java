package ru.yandex.metrika.userparams.sharder.config;

import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;
import org.springframework.context.annotation.Import;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.consumer.SyncConsumer;
import ru.yandex.kikimr.persqueue.consumer.sync.SyncConsumerConfig;
import ru.yandex.metrika.lb.read.processing.LogbrokerSimpleProcessor;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStatRegistrator;
import ru.yandex.metrika.lb.serialization.BatchSerializer;
import ru.yandex.metrika.lb.waitable.WaitingLogbrokerConfig;
import ru.yandex.metrika.lb.waitable.WaitingLogbrokerWriter;
import ru.yandex.metrika.lb.write.LogbrokerWriter;
import ru.yandex.metrika.lb.write.LogbrokerWriterConfig;
import ru.yandex.metrika.lb.write.LogbrokerWriterFactory;
import ru.yandex.metrika.userparams.ListParamWrapper;

@Import({
        UserparamsSharderConfig.class,
        UserParamsSharderStepsConfig.class,
        WaitingLogbrokerConfig.class
})
@Configuration
@EnableAspectJAutoProxy(proxyTargetClass = true)
public class UserParamsSharderTestConfig {

    @Bean
    public WaitingLogbrokerWriter<ListParamWrapper> inputWriter(LogbrokerWriter<ListParamWrapper> delegate, LogbrokerSimpleProcessor<ListParamWrapper> processor, ProcessedMessagesStatRegistrator processedMessagesStatRegistrator) {
        return new WaitingLogbrokerWriter<>(delegate, processor, processedMessagesStatRegistrator);
    }


    @Bean
    public LogbrokerWriter<ListParamWrapper> userparamsLogbrokerWriter(LogbrokerWriterFactory factory,
                                                                       BatchSerializer<ListParamWrapper> serializer,
                                                                       @Qualifier("userparamsLogbrokerWriterConfig") LogbrokerWriterConfig logbrokerWriterConfig) {
        return factory.reinitializingLogbrokerWriter(
                logbrokerWriterConfig,
                serializer);
    }

    @Bean
    public LogbrokerWriterConfig userparamsLogbrokerWriterConfig() {
        var config = new LogbrokerWriterConfig();
        config.setTopic(UserParamsSharderSettings.getUserapramsTopic());
        config.setSourceIdPrefix(UserParamsSharderSettings.getUserparamsSharderSourceId());
        return config;
    }

    @Bean
    public SyncConsumer inputConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory,
                                      @Qualifier("inputConsumerConfig") SyncConsumerConfig ordersSyncConsumerConfig) throws InterruptedException, TimeoutException, ExecutionException {
        var syncConsumer = logbrokerClientAsyncFactory.syncConsumer(ordersSyncConsumerConfig).get();
        syncConsumer.init();
        return syncConsumer;
    }

    @Bean
    public SyncConsumer outputConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory,
                                       @Qualifier("outputConsumerConfig") SyncConsumerConfig ordersSyncConsumerConfig) throws InterruptedException, TimeoutException, ExecutionException {
        var syncConsumer = logbrokerClientAsyncFactory.syncConsumer(ordersSyncConsumerConfig).get();
        syncConsumer.init();
        return syncConsumer;
    }

    @Bean
    public SyncConsumerConfig inputConsumerConfig() {
        return getSyncConsumerConfig(UserParamsSharderSettings.getUserapramsTopic(), "test-input-consumer");
    }

    @Bean
    public SyncConsumerConfig outputConsumerConfig() {
        return getSyncConsumerConfig(UserParamsSharderSettings.getUserparamsUpdatesTopic(), "consumer");
    }


    private SyncConsumerConfig getSyncConsumerConfig(String topic, String consumerPath) {
        return SyncConsumerConfig
                .builder(List.of(topic), consumerPath)
                .setReadDataTimeout(3, TimeUnit.SECONDS)
                .configureReader(x -> x.setMaxCount(0))
                .build();
    }
}

