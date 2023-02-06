package ru.yandex.metrika.internalapid.api.management.client.controllercontext;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;

import ru.yandex.metrika.internalapid.common.GoalsController;
import ru.yandex.metrika.spring.configuration.MockMvcConfigurationSupport;
import ru.yandex.metrika.spring.params.DeletedAspect;

@Configuration
@EnableAspectJAutoProxy(proxyTargetClass = true)
public class GoalsControllerCommonContext extends MockMvcConfigurationSupport {

    @Bean
    public GoalsController goalsController() {
        return new GoalsController();
    }

    @Bean
    public DeletedAspect deletedAspect() {
        return new DeletedAspect();
    }
}

