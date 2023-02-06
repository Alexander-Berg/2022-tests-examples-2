package ru.yandex.metrika.api.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.metrika.api.constructor.contr.FeatureService;
import ru.yandex.metrika.api.management.tests.util.FeatureServiceMock;

@Configuration
public class FeatureServiceConfig {

    @Bean
    FeatureService featureService() {
        return new FeatureServiceMock();
    }
}
