package ru.yandex.metrika.cdp.chwriter.spring;


import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ImportResource;

@Configuration
@ImportResource(
        locations = {
                "classpath:/ru/yandex/metrika/cdp/chwriter/cdp-ch-writer.xml",
                "classpath:/ru/yandex/metrika/util/common-jdbc.xml",
                "classpath:/ru/yandex/metrika/cdp/chwriter/tests/medium/steps/cdp-ch-writer-steps.xml"
        }
)
public class CdpChWriterConfig {
}
