package ru.yandex.metrika.userparams2d.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;

import ru.yandex.commune.bazinga.impl.storage.BazingaStorage;
import ru.yandex.commune.bazinga.impl.storage.memory.InMemoryBazingaStorage;
import ru.yandex.commune.zk2.ZkPath;
import ru.yandex.commune.zk2.primitives.observer.ZkPathObserver;

import static org.mockito.Mockito.mock;

@Configuration
@ComponentScan("ru.yandex.metrika.userparams2d.steps")
public class UserParamsStepsConfig {

    @Bean
    public BazingaStorage bazingaStorage() {
        return new InMemoryBazingaStorage();
    }

     @Bean
     public ZkPathObserver zkPathObserver() {
         return mock(ZkPathObserver.class);
     }

    @Bean
    public ZkPath zkPath() {
        return new ZkPath("/test");
    }
}

