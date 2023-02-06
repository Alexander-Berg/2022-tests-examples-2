package ru.yandex.metrika.cdp.api.validation;

import java.time.ZoneOffset;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.metrika.cdp.api.InMemoryListsChecker;
import ru.yandex.metrika.cdp.services.CounterTimezoneProvider;
import ru.yandex.metrika.cdp.validation.ListsChecker;
import ru.yandex.metrika.cdp.validation.ValidationHelper;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

@Configuration
public class ValidationTestConfig {

    @Bean
    public LocaleDictionaries localeDictionaries() {
        return new LocaleDictionaries();
    }

    @Bean(name = "testAttributesValidationHelper")
    public ValidationHelper attributesValidationHelper(@Qualifier("inMemoryListsChecker") ListsChecker listsChecker,
                                                       CounterTimezoneProvider counterTimezoneProvider,
                                                       LocaleDictionaries localeDictionaries) {
        return new ValidationHelper(listsChecker, counterTimezoneProvider, localeDictionaries);
    }

    @Bean
    public InMemoryListsChecker inMemoryListsChecker() {
        return new InMemoryListsChecker();
    }

    @Bean(name = "testCounterTimezoneProvider")
    public CounterTimezoneProvider counterTimezoneProvider() {
        return counterId -> ZoneOffset.UTC;
    }

}
