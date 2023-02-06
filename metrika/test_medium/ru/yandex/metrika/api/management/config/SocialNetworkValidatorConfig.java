package ru.yandex.metrika.api.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.management.client.SocialNetworkService;
import ru.yandex.metrika.api.management.client.utils.SocialNetworkValidator;

@Configuration
@Import(SocialNetworkServiceConfig.class)
public class SocialNetworkValidatorConfig {

    @Bean
    public SocialNetworkValidator socialNetworkValidator(SocialNetworkService socialNetworkService) {
        return new SocialNetworkValidator(socialNetworkService);
    }
}
