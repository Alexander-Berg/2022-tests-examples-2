package ru.yandex.metrika.api.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.ydb.YdbClientProperties;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.YdbSessionManager;

@Configuration
public class CounterStatYdbTemplateConfig {

    @Bean
    YdbClientProperties ydbClientProperties() {
        var ydbClientProperties = new YdbClientProperties();
        ydbClientProperties.setSessionPoolMinSize(10);
        ydbClientProperties.setSessionPoolMaxSize(50);
        ydbClientProperties.setEndpoint(EnvironmentHelper.ydbEndpoint);
        ydbClientProperties.setDatabase(EnvironmentHelper.ydbDatabase);
        return ydbClientProperties;
    }

    @Bean
    YdbSessionManager counterStatSessionManager(YdbClientProperties ydbClientProperties) {
        return new YdbSessionManager(ydbClientProperties);
    }

    @Bean
    public YdbTemplate counterStatYdbTemplate(YdbSessionManager ydbSessionManager) {
        return new YdbTemplate(ydbSessionManager);
    }
}
