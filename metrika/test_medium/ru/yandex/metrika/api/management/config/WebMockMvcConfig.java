package ru.yandex.metrika.api.management.config;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.web.method.support.HandlerMethodArgumentResolver;
import org.springframework.web.servlet.config.annotation.ContentNegotiationConfigurer;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import ru.yandex.metrika.api.error.DefaultExceptionHandler;
import ru.yandex.metrika.api.error.MetrikaExceptionHandler;
import ru.yandex.metrika.spring.MetrikaApiMessageConverter;
import ru.yandex.metrika.spring.auth.CurrentUserHandlerMethodArgumentResolver;
import ru.yandex.metrika.spring.auth.TargetUserHandlerMethodArgumentResolver;
import ru.yandex.metrika.spring.export.ErrorResponseMessageConverter;
import ru.yandex.metrika.spring.params.ListArgumentResolver;

@Configuration
@Import(value = {
        MessageConvertersConfig.class
})
@EnableWebMvc
public class WebMockMvcConfig implements WebMvcConfigurer {
    @Autowired
    private MetrikaApiMessageConverter messageConverter;

    @Autowired
    private ErrorResponseMessageConverter errorConverter;

    @Override
    public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
        converters.add(messageConverter);
        converters.add(errorConverter);
    }

    @Override
    public void configureContentNegotiation(ContentNegotiationConfigurer configurer) {
        configurer.favorPathExtension(true);
        configurer.ignoreAcceptHeader(true);
        configurer.mediaTypes(Map.of("json", MediaType.parseMediaType("application/json; charset=utf-8")));
        configurer.defaultContentType(MediaType.valueOf("application/json; charset=utf-8"));
    }

    @Override
    public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
        System.out.println("addArgumentResolver");
        resolvers.add(getCurrentUserHandlerMethodArgumentResolver());
        resolvers.add(getTargetUserHandlerMethodArgumentResolver());
        resolvers.add(new ListArgumentResolver());
    }

    @Bean
    public DefaultExceptionHandler exceptionHandler() {
        return new MetrikaExceptionHandler();
    }

    @Bean
    public CurrentUserHandlerMethodArgumentResolver getCurrentUserHandlerMethodArgumentResolver() {
        return new CurrentUserHandlerMethodArgumentResolver();
    }

    @Bean
    public TargetUserHandlerMethodArgumentResolver getTargetUserHandlerMethodArgumentResolver() {
        return new TargetUserHandlerMethodArgumentResolver();
    }
}
