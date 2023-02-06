package ru.yandex.metrika.api.management.config;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.jdbc.core.JdbcTemplate;

import ru.yandex.metrika.api.management.client.recommendations.RecommendationMetaDao;

@Configuration
@Import(JdbcTemplateConfig.class)
public class RecommendationDaoConfig {

    @Bean
    public RecommendationMetaDao recommendationDao(@Qualifier("pgSubscriptionsTemplate") JdbcTemplate pgSubscriptionsTemplate) {
        return new RecommendationMetaDao(pgSubscriptionsTemplate);
    }
}
