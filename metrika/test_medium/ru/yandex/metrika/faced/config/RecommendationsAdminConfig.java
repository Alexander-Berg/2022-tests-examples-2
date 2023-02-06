package ru.yandex.metrika.faced.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import ru.yandex.metrika.api.management.admin.RecommendationsAdminController;
import ru.yandex.metrika.api.management.admin.RecommendationsAdminService;
import ru.yandex.metrika.api.management.client.recommendations.RecommendationMetaDao;
import ru.yandex.metrika.api.management.config.RecommendationDaoConfig;
import ru.yandex.metrika.api.management.config.WebMockMvcConfig;

@Configuration
@Import(value = {
        RecommendationDaoConfig.class,
        WebMockMvcConfig.class
})
@EnableAsync
public class RecommendationsAdminConfig implements WebMvcConfigurer {

    @Bean
    public RecommendationsAdminService recommendationsAdminService(RecommendationMetaDao recommendationMetaDao) {
        return new RecommendationsAdminService(recommendationMetaDao);
    }

    @Bean
    public RecommendationsAdminController recommendationsAdminController() {
        return new RecommendationsAdminController();
    }
}
