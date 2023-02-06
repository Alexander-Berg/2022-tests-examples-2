package ru.yandex.metrika.api.management.client;

import java.util.List;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter;
import org.springframework.web.method.support.HandlerMethodArgumentResolver;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurationSupport;

import ru.yandex.metrika.api.error.DefaultExceptionHandler;
import ru.yandex.metrika.spring.params.RenamingProcessor;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

@Configuration
public class ExpenseUploadingControllerCommonContext extends WebMvcConfigurationSupport {

    @Bean
    public ExpenseUploadingController expenseUploadingController() throws Exception {
        return new ExpenseUploadingController();
    }

    @Bean
    public DefaultExceptionHandler defaultExceptionHandler() {
        return new DefaultExceptionHandler();
    }

    @Bean
    public LocaleDictionaries localeDictionaries() {
        return new LocaleDictionaries();
    }

    @Bean
    public RenamingProcessor renamingProcessor() {
        return new RenamingProcessor(true);
    }

    @Override
    public void addArgumentResolvers(List<HandlerMethodArgumentResolver> argumentResolvers) {
        argumentResolvers.add(renamingProcessor());
    }

    @Override
    public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
        converters.add(new MappingJackson2HttpMessageConverter());
    }

}
