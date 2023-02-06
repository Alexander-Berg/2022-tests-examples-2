package ru.yandex.metrika.api.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.metrika.api.management.client.recommendations.RecommendationYdbDao;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.ydb.YdbClientProperties;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.YdbSessionManager;

@Configuration
public class RecommendationYdbDaoConfig {

    @Bean
    public YdbClientProperties ydbClientProperties() {
        var ydbClientProperties = new YdbClientProperties();
        ydbClientProperties.setEndpoint(EnvironmentHelper.ydbEndpoint);
        ydbClientProperties.setDatabase(EnvironmentHelper.ydbDatabase);
        return ydbClientProperties;
    }

    @Bean
    public YdbSessionManager ydbSessionManager(YdbClientProperties ydbClientProperties) {
        return new YdbSessionManager(ydbClientProperties);
    }

    @Bean
    public YdbTemplate ydbTemplate(YdbSessionManager ydbSessionManager) {
        return new YdbTemplate(ydbSessionManager);
    }

    @Bean
    public RecommendationYdbDao recommendationYdbDao(YdbTemplate ydbTemplate) {
        return new RecommendationYdbDao(ydbTemplate);
    }
}
