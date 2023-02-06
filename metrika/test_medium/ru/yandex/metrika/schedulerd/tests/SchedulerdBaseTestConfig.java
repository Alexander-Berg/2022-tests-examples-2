package ru.yandex.metrika.schedulerd.tests;

import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ImportResource;

@ImportResource(locations = {
        "/ru/yandex/metrika/schedulerd/steps/schedulerd-steps.xml",
        "/ru/yandex/metrika/util/common-jmx-support.xml",
        "/ru/yandex/metrika/util/common-jdbc.xml",
})
@Configuration
public class SchedulerdBaseTestConfig {
}
