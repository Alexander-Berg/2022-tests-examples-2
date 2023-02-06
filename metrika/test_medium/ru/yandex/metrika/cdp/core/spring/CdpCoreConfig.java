package ru.yandex.metrika.cdp.core.spring;


import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ImportResource;

@Configuration
@ImportResource(
        locations = {
                "classpath:/ru/yandex/metrika/cdp/core/cdp-core.xml",
                "classpath:/ru/yandex/metrika/util/common-jdbc.xml",
                "classpath:/ru/yandex/metrika/cdp/core/tests/medium/steps/cdp-core-steps.xml"
        }
)
public class CdpCoreConfig {
}
