package ru.yandex.metrika.faced.config;

import java.util.List;

import org.mockito.Mockito;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.web.method.support.HandlerMethodArgumentResolver;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import ru.yandex.metrika.api.management.client.RecommendationsController;
import ru.yandex.metrika.api.management.client.recommendations.RecommendationService;
import ru.yandex.metrika.api.management.config.WebMockMvcConfig;
import ru.yandex.metrika.spring.params.ListArgumentResolver;

@Configuration
@Import(value = {
        WebMockMvcConfig.class
})
@EnableAsync
public class UserRecommendationConfig implements WebMvcConfigurer {

    @Override
    public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
        resolvers.add(new ListArgumentResolver());
    }


    @Bean
    public RecommendationService mockRecommendationService() {
        return Mockito.mock(RecommendationService.class);
    }

    @Bean
    public RecommendationsController recommendationsAdminController() {
        return new RecommendationsController();
    }
}
