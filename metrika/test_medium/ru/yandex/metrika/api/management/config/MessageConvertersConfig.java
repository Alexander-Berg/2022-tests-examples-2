package ru.yandex.metrika.api.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.error.BackendError;
import ru.yandex.metrika.rbac.RoleResolver;
import ru.yandex.metrika.rbac.metrika.MetrikaRoleResolver;
import ru.yandex.metrika.spring.MetrikaApiMessageConverter;
import ru.yandex.metrika.spring.ViewResolver;
import ru.yandex.metrika.spring.export.ErrorResponseMessageConverter;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

@Configuration
@Import(value = {
        LocaleDictionariesConfig.class
})
public class MessageConvertersConfig {
    @Bean
    public RoleResolver roleResolver() {
        return new MetrikaRoleResolver();
    }

    @Bean
    public ViewResolver viewResolver(RoleResolver roleResolver) {
        ViewResolver bean = new ViewResolver();
        bean.setRoleResolver(roleResolver);
        return bean;
    }

    @Bean
    public BackendError backendError(LocaleDictionaries localeDictionaries) {
        BackendError bean = new BackendError();
        bean.setLocaleDictionaries(localeDictionaries);
        return bean;
    }

    @Bean
    public MetrikaApiMessageConverter metrikaApiMessageConverter(LocaleDictionaries dictionaries,
                                                                 ViewResolver viewResolver,
                                                                 BackendError backendError) {
        MetrikaApiMessageConverter bean = new MetrikaApiMessageConverter();
        bean.setLocaleDictionaries(dictionaries);
        bean.setUnwrapRootValue(false);
        bean.setViewResolver(viewResolver);
        bean.setBackendError(backendError);
        return bean;
    }

    @Bean
    public ErrorResponseMessageConverter errorResponseMessageConverter(LocaleDictionaries dictionaries,
                                                                       ViewResolver viewResolver,
                                                                       BackendError backendError) {
        ErrorResponseMessageConverter bean = new ErrorResponseMessageConverter();
        bean.setLocaleDictionaries(dictionaries);
        bean.setViewResolver(viewResolver);
        bean.setBackendError(backendError);
        return bean;
    }
}
