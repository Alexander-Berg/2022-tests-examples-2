package ru.yandex.metrika.api.management.config;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.managers.CurrencyService;

@Configuration
@Import(JdbcTemplateConfig.class)
public class CurrencyServiceConfig {

    @Bean
    public CurrencyService currencyService(@Qualifier("convMainTemplate") MySqlJdbcTemplate convMainTemplate) {
        return new CurrencyService(convMainTemplate);
    }
}
