package ru.yandex.metrika.api.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.management.client.counter.CountersDao;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.managers.TimeZones;

@Configuration
@Import({JdbcTemplateConfig.class, TimeZonesConfig.class, CurrencyServiceConfig.class})
public class CountersDaoConfig {

    @Bean
    public CountersDao countersDao(MySqlJdbcTemplate convMainTemplate,
                                   TimeZones timeZones, CurrencyService currencyService) {
        return new CountersDao(convMainTemplate, timeZones, currencyService);
    }
}
