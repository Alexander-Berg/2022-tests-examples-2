package ru.yandex.metrika.api.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.management.client.MessengerService;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;

@Configuration
@Import(JdbcTemplateConfig.class)
public class MessengerServiceConfig {

    @Bean
    public MessengerService messengerService(MySqlJdbcTemplate convMainTemplate) {
        return new MessengerService(convMainTemplate);
    }
}
