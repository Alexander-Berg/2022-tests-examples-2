package ru.yandex.metrika.mobmet.crash.decoder.test.daemon.spring;

import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ImportResource;

@Configuration
@ImportResource({
        "/ru/yandex/metrika/mobmet/crash/decoder/crash-decoder.xml",
        "/ru/yandex/metrika/mobmet/crash/decoder/crash-decoder-cloud.xml",
        "/ru/yandex/metrika/util/common-jdbc-pg-mobile-crashes.xml",
        "/ru/yandex/metrika/mobmet/mobmet-common-crash.xml",
        "/ru/yandex/metrika/util/common-metrics-support.xml",
        "/ru/yandex/metrika/util/common-monitoring-support.xml",
        "/ru/yandex/metrika/util/common-jmx-support.xml",
        "/ru/yandex/metrika/util/common-console.xml",
        "/ru/yandex/metrika/util/common-tx.xml",
        "/ru/yandex/metrika/util/common-jdbc.xml",
        "/ru/yandex/metrika/util/juggler-reporter.xml",
        //Степы тестов
        "/ru/yandex/metrika/mobmet/crash/decoder/steps/mobmet-crash-decoder-steps.xml"
})
public class MobmetCrashDecoderTestConfig {
}
