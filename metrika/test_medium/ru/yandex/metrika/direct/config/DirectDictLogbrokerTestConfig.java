package ru.yandex.metrika.direct.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.producer.async.AsyncProducerConfig;
import ru.yandex.kikimr.persqueue.proxy.ProxyBalancer;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.lb.ClientAsyncFactory;
import ru.yandex.metrika.lb.read.AbstractLogbrokerConsumerConfig;
import ru.yandex.metrika.lb.read.GeneralLogbrokerConsumerConfig;
import ru.yandex.metrika.lb.read.LogbrokerConsumerFactory;
import ru.yandex.metrika.lb.serialization.proto.GenericProtoSerializer;
import ru.yandex.metrika.lb.serialization.proto.ProtoSerializer;
import ru.yandex.metrika.lb.serialization.protoseq.ProtoSeqBatchSerializer;

import static metrika.AdvClickDictionaryUpdate.TBanner;
import static metrika.AdvClickDictionaryUpdate.TBannerGroup;
import static metrika.AdvClickDictionaryUpdate.TOrderPhrase;
import static metrika.AdvClickDictionaryUpdate.TSmartOrderTargetPhrase;
import static metrika.AdvClickDictionaryUpdate.TTargetPhrase;

@Configuration
public class DirectDictLogbrokerTestConfig {

    private final String bannerGroupTestTopic = "/test/banner-group-log";
    private final String bannerTestTopic = "/test/banner-log";
    private final String phrasesTestTopic = "/test/order-phrases-log";
    private final String targetPhrasesTestTopic = "/test/target-phrases-log";
    private final String smartOrderTargetPhrasesTestTopic = "/test/smart-order-target-phrase-log";

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
    public AsyncProducerConfig bannerGroupsProducerConfig() {
        return AsyncProducerConfig.builder(bannerGroupTestTopic, "some_writer".getBytes())
                .build();
    }

    @Bean
    public AsyncProducerConfig bannersProducerConfig() {
        return AsyncProducerConfig.builder(bannerTestTopic, "some_writer".getBytes())
                .build();
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

        config.setPoolName("direct-lb-test-reader");
        config.setPoolMaxCoreSize(4);

        return config;
    }

    @Bean
    public AbstractLogbrokerConsumerConfig bannerGroupsConsumerConfig() {
        var config = createDefaultTestConfig();

        config.setTopicPath(bannerGroupTestTopic);
        config.setConsumerPath("/test/consumer");

        return config;
    }

    @Bean
    public AbstractLogbrokerConsumerConfig bannersConsumerConfig() {
        var config = createDefaultTestConfig();

        config.setTopicPath(bannerTestTopic);
        config.setConsumerPath("/test/consumer");

        return config;
    }

    @Bean
    public ProtoSerializer<TBannerGroup> bannerGroupsProtoSerializer() {
        return new GenericProtoSerializer<>(TBannerGroup.parser());
    }

    @Bean
    public ProtoSeqBatchSerializer<TBannerGroup> protoSeqBannerGroupsSerializer(
            ProtoSerializer<TBannerGroup> bannerGroupsProtoSerializer
    ) {
        return new ProtoSeqBatchSerializer<>(bannerGroupsProtoSerializer);
    }

    @Bean
    public ProtoSerializer<TBanner> bannersProtoSerializer() {
        return new GenericProtoSerializer<>(TBanner.parser());
    }

    @Bean
    public ProtoSeqBatchSerializer<TBanner> protoSeqBannersSerializer(
            ProtoSerializer<TBanner> bannersProtoSerializer
    ) {
        return new ProtoSeqBatchSerializer<>(bannersProtoSerializer);
    }

    @Bean
    public AsyncProducerConfig phrasesProducerConfig() {
        return AsyncProducerConfig.builder(phrasesTestTopic, "some_writer".getBytes())
                .build();
    }

    @Bean
    public AbstractLogbrokerConsumerConfig phrasesConsumerConfig() {
        var config = createDefaultTestConfig();

        config.setTopicPath(phrasesTestTopic);
        config.setConsumerPath("/test/consumer");

        return config;
    }

    @Bean
    public ProtoSerializer<TOrderPhrase> phrasesProtoSerializer() {
        return new GenericProtoSerializer<>(TOrderPhrase.parser());
    }

    @Bean
    public ProtoSeqBatchSerializer<TOrderPhrase> protoSeqPhrasesSerializer(
            ProtoSerializer<TOrderPhrase> phrasesProtoSerializer
    ) {
        return new ProtoSeqBatchSerializer<>(phrasesProtoSerializer);
    }

    @Bean
    public AsyncProducerConfig targetPhrasesProducerConfig() {
        return AsyncProducerConfig.builder(targetPhrasesTestTopic, "some_writer".getBytes())
                .build();
    }

    @Bean
    public AbstractLogbrokerConsumerConfig targetPhrasesConsumerConfig() {
        var config = createDefaultTestConfig();

        config.setTopicPath(targetPhrasesTestTopic);
        config.setConsumerPath("/test/consumer");

        return config;
    }

    @Bean
    public ProtoSerializer<TTargetPhrase> targetPhrasesProtoSerializer() {
        return new GenericProtoSerializer<>(TTargetPhrase.parser());
    }

    @Bean
    public ProtoSeqBatchSerializer<TTargetPhrase> protoSeqTargetPhrasesSerializer(
            ProtoSerializer<TTargetPhrase> targetPhrasesProtoSerializer
    ) {
        return new ProtoSeqBatchSerializer<>(targetPhrasesProtoSerializer);
    }

    @Bean
    public AsyncProducerConfig smartOrderTargetPhrasesProducerConfig() {
        return AsyncProducerConfig.builder(smartOrderTargetPhrasesTestTopic, "some_writer".getBytes())
                .build();
    }

    @Bean
    public AbstractLogbrokerConsumerConfig smartOrderTargetPhrasesConsumerConfig() {
        var config = createDefaultTestConfig();

        config.setTopicPath(smartOrderTargetPhrasesTestTopic);
        config.setConsumerPath("/test/consumer");

        return config;
    }

    @Bean
    public ProtoSerializer<TSmartOrderTargetPhrase> smartOrderTargetPhrasesProtoSerializer() {
        return new GenericProtoSerializer<>(TSmartOrderTargetPhrase.parser());
    }

    @Bean
    public ProtoSeqBatchSerializer<TSmartOrderTargetPhrase> protoSeqSmartOrderTargetPhrasesSerializer(
            ProtoSerializer<TSmartOrderTargetPhrase> smartOrderTargetPhrasesProtoSerializer
    ) {
        return new ProtoSeqBatchSerializer<>(smartOrderTargetPhrasesProtoSerializer);
    }
}
