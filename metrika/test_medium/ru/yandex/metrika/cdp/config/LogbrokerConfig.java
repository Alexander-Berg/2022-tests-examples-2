package ru.yandex.metrika.cdp.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.proxy.ProxyBalancer;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.lb.write.LogbrokerWriterFactory;

@Configuration
public class LogbrokerConfig {
    @Bean
    public ProxyBalancer proxyBalancer() {
        return new ProxyBalancer(EnvironmentHelper.logbrokerHost,
                EnvironmentHelper.logbrokerPort,
                EnvironmentHelper.logbrokerPort);
    }

    @Bean
    public LogbrokerClientAsyncFactory logbrokerClientAsyncFactory(ProxyBalancer proxyBalancer) {
        return new LogbrokerClientAsyncFactory(proxyBalancer);
    }

    @Bean
    public LogbrokerWriterFactory logbrokerWriterFactory(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory) {
        return new LogbrokerWriterFactory(logbrokerClientAsyncFactory);
    }
}
