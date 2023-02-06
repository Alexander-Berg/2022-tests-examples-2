package ru.yandex.metrika.api.management.config;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.management.client.counter.CounterOptionsDao;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;

@Configuration
@Import(JdbcTemplateConfig.class)
public class CounterOptionsDaoConfig {

    @Bean
    CounterOptionsDao counterOptionsDao(@Qualifier("convMainTemplate") MySqlJdbcTemplate convMainTemplate) {
        return new CounterOptionsDao(convMainTemplate);
    }
}
