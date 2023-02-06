package ru.yandex.metrika.api.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.metrika.util.locale.LocaleDictionaries;

@Configuration
public class LocaleDictionariesConfig {

    @Bean
    public LocaleDictionaries localeDictionaries() {
        return new LocaleDictionaries();
    }
}
