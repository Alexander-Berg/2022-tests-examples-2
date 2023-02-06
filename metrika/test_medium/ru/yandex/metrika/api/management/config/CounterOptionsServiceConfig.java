package ru.yandex.metrika.api.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.management.client.counter.CounterOptionsDao;
import ru.yandex.metrika.api.management.client.counter.CounterOptionsService;

@Configuration
@Import(CounterOptionsDaoConfig.class)
public class CounterOptionsServiceConfig {

    @Bean
    public CounterOptionsService counterOptionsService(CounterOptionsDao counterOptionsDao) {
        return new CounterOptionsService(counterOptionsDao);
    }
}
