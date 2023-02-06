package ru.yandex.metrika.api.management.config;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.management.client.OfflineOptionsService;
import ru.yandex.metrika.api.management.client.counter.CounterOptionsService;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.managers.TimeZones;

@Configuration
@Import({JdbcTemplateConfig.class, TimeZonesConfig.class, CounterOptionsServiceConfig.class})
public class OfflineOptionsServiceConfig {

    @Bean
    public OfflineOptionsService offlineOptionsService(@Qualifier("convMainTemplate") MySqlJdbcTemplate convMain,
                                                       TimeZones timeZones,
                                                       CounterOptionsService counterOptionsService) {
        return new OfflineOptionsService(
                convMain, timeZones, counterOptionsService
        );
    }
}
