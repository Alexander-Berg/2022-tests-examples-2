package ru.yandex.metrika.api.management.config;

import javax.validation.Validator;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;

import ru.yandex.metrika.util.ApiInputValidator;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

@Configuration
public class ApiValidatorConfig {

    @Bean
    public Validator validator() {
        return new LocalValidatorFactoryBean();
    }

    @Bean
    public LocaleDictionaries localeDictionaries() {
        return new LocaleDictionaries();
    }

    @Bean
    public ApiInputValidator apiInputValidator() {
        return new ApiInputValidator(validator(), localeDictionaries());
    }
}
