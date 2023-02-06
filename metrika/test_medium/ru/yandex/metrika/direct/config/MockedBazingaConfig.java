package ru.yandex.metrika.direct.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.commune.bazinga.impl.storage.BazingaStorage;
import ru.yandex.commune.zk2.ZkPath;
import ru.yandex.commune.zk2.primitives.observer.ZkPathObserver;

import static org.mockito.Mockito.mock;

@Configuration
public class MockedBazingaConfig {
    @Bean
    public BazingaStorage mockedBazinga() {
        return mock(BazingaStorage.class);
    }

    @Bean
    public ZkPathObserver mockedZkPathObserver() {
        return mock(ZkPathObserver.class);
    }

    @Bean
    public ZkPath zkPath() {
        return new ZkPath("/test");
    }
}
