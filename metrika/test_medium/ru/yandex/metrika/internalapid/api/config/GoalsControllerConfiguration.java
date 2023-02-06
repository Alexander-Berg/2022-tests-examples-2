package ru.yandex.metrika.internalapid.api.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.internalapid.api.management.client.controllercontext.GoalsControllerCommonContext;

@Configuration
@Import(GoalsControllerCommonContext.class)
public class GoalsControllerConfiguration {

}
