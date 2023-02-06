package ru.yandex.metrika.cdp.chwriter.spring;


import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.cdp.config.LogbrokerConfig;
import ru.yandex.metrika.cdp.dto.core.ClientKey;
import ru.yandex.metrika.cdp.dto.core.OrderKey;
import ru.yandex.metrika.lb.read.processing.LogbrokerFilteringProcessor;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStatRegistrator;
import ru.yandex.metrika.lb.serialization.Serializer;
import ru.yandex.metrika.lb.waitable.WaitingLogbrokerConfig;
import ru.yandex.metrika.lb.waitable.WaitingLogbrokerWriter;
import ru.yandex.metrika.lb.write.LogbrokerWriter;
import ru.yandex.metrika.lb.write.LogbrokerWriterConfig;
import ru.yandex.metrika.lb.write.LogbrokerWriterFactory;

@Configuration
@Import({
        CdpChWriterConfig.class,
        CdpChWriterYdbTestConfig.class,
        LogbrokerConfig.class,
        WaitingLogbrokerConfig.class
})
@EnableAspectJAutoProxy(proxyTargetClass = true)
public class CdpChWriterTestConfig {

    @Bean
    public WaitingLogbrokerWriter<OrderKey> orderKeyWriter(LogbrokerWriter<OrderKey> delegate, LogbrokerFilteringProcessor<OrderKey> processor, ProcessedMessagesStatRegistrator processedMessagesStatRegistrator) {
        return new WaitingLogbrokerWriter<>(delegate, processor, processedMessagesStatRegistrator);
    }

    @Bean
    public WaitingLogbrokerWriter<ClientKey> clientKeyWriter(LogbrokerWriter<ClientKey> delegate, LogbrokerFilteringProcessor<ClientKey> processor, ProcessedMessagesStatRegistrator processedMessagesStatRegistrator) {
        return new WaitingLogbrokerWriter<>(delegate, processor, processedMessagesStatRegistrator);
    }

    @Bean
    public LogbrokerWriter<OrderKey> orderKeyLogbrokerWriter(LogbrokerWriterFactory factory,
                                                             Serializer<OrderKey> serializer,
                                                             @Qualifier("orderKeyLogbrokerWriterConfig") LogbrokerWriterConfig orderKeysDownstreamConfig) {

        return factory.reinitializingLogbrokerWriter(
                orderKeysDownstreamConfig,
                serializer
        );
    }

    @Bean
    public LogbrokerWriter<ClientKey> clientKeyLogbrokerWriter(LogbrokerWriterFactory factory,
                                                               Serializer<ClientKey> serializer,
                                                               @Qualifier("clientKeyLogbrokerWriterConfig") LogbrokerWriterConfig clientKeysDownstreamConfig) {
        return factory.reinitializingLogbrokerWriter(
                clientKeysDownstreamConfig,
                serializer
        );
    }

    @Bean
    public LogbrokerWriterConfig clientKeyLogbrokerWriterConfig() {
        var config = new LogbrokerWriterConfig();
        config.setTopic("updated-clients-topic");
        config.setSourceIdPrefix("cdp-core-writer-source");
        return config;
    }

    @Bean
    public LogbrokerWriterConfig orderKeyLogbrokerWriterConfig() {
        var config = new LogbrokerWriterConfig();
        config.setTopic("updated-orders-topic");
        config.setSourceIdPrefix("cdp-core-writer-source");
        return config;
    }
}
