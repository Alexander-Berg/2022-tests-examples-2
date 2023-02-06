package ru.yandex.metrika.internalapid.api.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.management.config.WebMockMvcConfig;
import ru.yandex.metrika.internalapid.api.management.client.controllercontext.CoreControllerContext;

@Configuration
@Import({WebMockMvcConfig.class, CoreControllerContext.class})
public class CoreControllerConfiguration {
}
