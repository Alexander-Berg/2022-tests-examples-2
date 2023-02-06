package ru.yandex.metrika.api.management.config;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.management.client.SocialNetworkService;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;

@Configuration
@Import(JdbcTemplateConfig.class)
public class SocialNetworkServiceConfig {

    @Bean
    public SocialNetworkService socialNetworkService(@Qualifier("convMainTemplate") MySqlJdbcTemplate convMainTemplate) {
        return new SocialNetworkService(convMainTemplate);
    }
}
