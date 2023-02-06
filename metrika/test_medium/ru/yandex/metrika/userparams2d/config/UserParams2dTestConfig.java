package ru.yandex.metrika.userparams2d.config;

import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import com.fasterxml.jackson.core.type.TypeReference;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.FilterType;
import org.springframework.context.annotation.Import;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.consumer.SyncConsumer;
import ru.yandex.kikimr.persqueue.consumer.sync.SyncConsumerConfig;
import ru.yandex.kikimr.persqueue.proxy.ProxyBalancer;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamUpdate;
import ru.yandex.metrika.common.test.medium.CalcCloudSteps;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStatRegistrator;
import ru.yandex.metrika.lb.serialization.Serializer;
import ru.yandex.metrika.lb.serialization.json.JsonDtoSerializer;
import ru.yandex.metrika.lb.waitable.WaitingLogbrokerConfig;
import ru.yandex.metrika.lb.waitable.WaitingLogbrokerWriter;
import ru.yandex.metrika.lb.write.LogbrokerWriter;
import ru.yandex.metrika.lb.write.LogbrokerWriterConfig;
import ru.yandex.metrika.lb.write.LogbrokerWriterFactory;
import ru.yandex.metrika.userparams.UserParamLBCHRow;
import ru.yandex.metrika.userparams2d.processing.InvalidatingCacheLogbrokerProcessor;

@Configuration
@Import({UserParams2dConfig.class, UserParamsStepsConfig.class, WaitingLogbrokerConfig.class})
@ComponentScan(
        basePackages = {"ru.yandex.metrika.common.test.medium"},
        excludeFilters = @ComponentScan.Filter(
                type = FilterType.ASSIGNABLE_TYPE,
                value = CalcCloudSteps.class
        )
)
public class UserParams2dTestConfig {

    @Bean
    public UserParamsSettings testSettings() {
        return new UserParamsSettings();
    }

    @Bean
    public Serializer<UserParamLBCHRow> lbchRowSerializer() {
        return new JsonDtoSerializer<>(new TypeReference<>() {});
    }

    @Bean
    public SyncConsumer outputGigaConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory,
                                           @Qualifier("outputGigaConsumerConfig") SyncConsumerConfig consumerConfig) throws InterruptedException, TimeoutException, ExecutionException {
        var syncConsumer = logbrokerClientAsyncFactory.syncConsumer(consumerConfig).get();
        syncConsumer.init();
        return syncConsumer;
    }

    @Bean
    public SyncConsumer outputNanoConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory,
                                           @Qualifier("outputNanoConsumerConfig") SyncConsumerConfig consumerConfig) throws InterruptedException, TimeoutException, ExecutionException {
        var syncConsumer = logbrokerClientAsyncFactory.syncConsumer(consumerConfig).get();
        syncConsumer.init();
        return syncConsumer;
    }


    @Bean
    public LogbrokerWriter<UserParamUpdate> inputWriter(LogbrokerWriterFactory factory,
                                                        Serializer<UserParamUpdate> serializer,
                                                        @Qualifier("inputLogbrokerWriterConfig") LogbrokerWriterConfig orderKeysDownstreamConfig) {
        return factory.reinitializingLogbrokerWriter(
                orderKeysDownstreamConfig,
                serializer
        );
    }

    @Bean
    public LogbrokerWriter<UserParamUpdate> apiInputWriter(LogbrokerWriterFactory factory,
                                                           Serializer<UserParamUpdate> serializer,
                                                           @Qualifier("apiInputLogbrokerWriterConfig") LogbrokerWriterConfig orderKeysDownstreamConfig) {
        return factory.reinitializingLogbrokerWriter(
                orderKeysDownstreamConfig,
                serializer
        );
    }

    @Bean
    public WaitingLogbrokerWriter<UserParamUpdate> waitingInputWriter(@Qualifier("inputWriter") LogbrokerWriter<UserParamUpdate> delegate, InvalidatingCacheLogbrokerProcessor<UserParamUpdate> processor, ProcessedMessagesStatRegistrator processedMessagesStatRegistrator) {
        return new WaitingLogbrokerWriter<>(delegate, processor, processedMessagesStatRegistrator);
    }

    @Bean
    public WaitingLogbrokerWriter<UserParamUpdate> waitingApiInputWriter(@Qualifier("apiInputWriter") LogbrokerWriter<UserParamUpdate> delegate, InvalidatingCacheLogbrokerProcessor<UserParamUpdate> processor, ProcessedMessagesStatRegistrator processedMessagesStatRegistrator) {
        return new WaitingLogbrokerWriter<>(delegate, processor, processedMessagesStatRegistrator);
    }

    @Bean
    public LogbrokerWriterConfig inputLogbrokerWriterConfig(UserParamsSettings settings) {
        var config = new LogbrokerWriterConfig();
        config.setTopic(settings.getUserparamUpdatesTopic());
        config.setSourceIdPrefix(settings.getCoreSourceId());
        return config;
    }


    @Bean
    public LogbrokerWriterConfig apiInputLogbrokerWriterConfig(UserParamsSettings settings) {
        var config = new LogbrokerWriterConfig();
        config.setTopic(settings.getUserparamUpdatesTopic());
        config.setSourceIdPrefix(settings.getApiSourceId());
        return config;
    }

    @Bean
    public LogbrokerClientAsyncFactory logbrokerClientAsyncFactory(ProxyBalancer proxyBalancer) {
        return new LogbrokerClientAsyncFactory(proxyBalancer);
    }

    @Bean
    public ProxyBalancer proxyBalancer() {
        return new ProxyBalancer(EnvironmentHelper.logbrokerHost,
                EnvironmentHelper.logbrokerPort,
                EnvironmentHelper.logbrokerPort);
    }

    @Bean
    public SyncConsumerConfig inputConsumerConfig(UserParamsSettings settings) {
        return getSyncConsumer(settings.getUserparamsUpdatesConsumerPath(), settings.getUserparamUpdatesTopic());
    }

    @Bean
    public SyncConsumerConfig outputGigaConsumerConfig(UserParamsSettings settings) {
        return getSyncConsumer(settings.getGigaLogConsumer(), settings.getUserparamsGigaTopic());
    }

    @Bean
    public SyncConsumerConfig outputNanoConsumerConfig(UserParamsSettings settings) {
        return getSyncConsumer(settings.getNanoLogConsumer(), settings.getUserparamsNanoTopic());
    }

    private SyncConsumerConfig getSyncConsumer(String consumerPath, String topic) {
        return SyncConsumerConfig
                .builder(List.of(topic), consumerPath)
                .setReadDataTimeout(3, TimeUnit.SECONDS)
                .configureReader(x -> x.setMaxCount(0))
                .build();
    }


}
