package ru.yandex.metrika.api.management.config;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.managers.TimeZones;

@Configuration
@Import(JdbcTemplateConfig.class)
public class TimeZonesConfig {

    @Bean
    public TimeZones timeZones(@Qualifier("convMainTemplate") MySqlJdbcTemplate convMainTemplate) {
        TimeZones timeZones = new TimeZones();
        timeZones.setTemplate(convMainTemplate);
        return timeZones;
    }
}
