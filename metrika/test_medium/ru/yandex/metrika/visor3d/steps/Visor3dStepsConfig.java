package ru.yandex.metrika.visor3d.steps;

import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.auth.Credentials;
import ru.yandex.kikimr.persqueue.consumer.SyncConsumer;
import ru.yandex.kikimr.persqueue.consumer.sync.SyncConsumerConfig;
import ru.yandex.metrika.filterd.process.EventLogCommon;
import ru.yandex.metrika.lb.read.processing.LogbrokerMessageProcessor;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStat;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStatRegistrator;
import ru.yandex.metrika.lb.waitable.WaitingLogbrokerConfig;

@Configuration
@Import(WaitingLogbrokerConfig.class)
public class Visor3dStepsConfig {

    @Bean
    public ProcessedMessagesStat processedMessagesStat(ProcessedMessagesStatRegistrator processedMessagesStatRegistrator, LogbrokerMessageProcessor<EventLogCommon> eventsProcessor) {
        return processedMessagesStatRegistrator.getStatForProcessor(eventsProcessor);
    }

    @Bean
    public SyncConsumer scrollsConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory, Visor3dSettings settings) throws ExecutionException, InterruptedException, TimeoutException {
        return getLogbrokerConsumer(logbrokerClientAsyncFactory, settings.getLogbrokerScrollsTopic());
    }

    @Bean
    public SyncConsumer eventsConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory, Visor3dSettings settings) throws ExecutionException, InterruptedException, TimeoutException {
        return getLogbrokerConsumer(logbrokerClientAsyncFactory, settings.getLogbrokerEventsTopic());
    }

    @Bean
    public SyncConsumer cryptaConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory, Visor3dSettings settings) throws ExecutionException, InterruptedException, TimeoutException {
        return getLogbrokerConsumer(logbrokerClientAsyncFactory, settings.getLogbrokerCryptaTopic());
    }


    private SyncConsumer getLogbrokerConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory, String topic) throws InterruptedException, TimeoutException, ExecutionException {
        SyncConsumer syncConsumer = logbrokerClientAsyncFactory.syncConsumer(getLogbrokerConsumerConfig(topic)).get();
        syncConsumer.init();
        return syncConsumer;
    }

    private SyncConsumerConfig getLogbrokerConsumerConfig(String topic) {
        return SyncConsumerConfig
                .builder(List.of(topic), "consumer")
                .setCredentialsProvider(Credentials::none)
                .setReadBufferSize(10000)
                .setReadDataTimeout(3, TimeUnit.SECONDS)
                .configureReader(reader -> reader
                        .setMaxCount(9999)
                        .setMaxSize(100000)
                        .setMaxUnconsumedReads(1000)
                        .setPartitionsAtOnce(99999)
                        .setMaxInflightReads(2)
                        .build()
                )
                .configureSession(session -> session
                        .setMaxReadMessagesCount(99999)
                        .setMaxReadPartitionsCount(9999)
                        .setMaxReadSize(99999)
                        .build()
                )
                .build();
    }
}
