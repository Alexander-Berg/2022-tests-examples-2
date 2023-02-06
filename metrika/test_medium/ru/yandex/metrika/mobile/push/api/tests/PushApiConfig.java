package ru.yandex.metrika.mobile.push.api.tests;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ImportResource;

import ru.yandex.metrika.clusters.clickhouse.MtMobGiga;
import ru.yandex.metrika.config.ArcadiaSourceAwareBeanDefinitionReader;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.managers.TimeZones;
import ru.yandex.metrika.mobmet.dao.ApplicationTimeZoneProvider;

@SuppressWarnings("SpringImportResource")
@Configuration
@ComponentScan("ru.yandex.metrika.mobile.push.api.steps")
@ImportResource(
        locations = {
                "classpath:ru/yandex/metrika/common-security-test.xml",
                "classpath:ru/yandex/metrika/util/common-jmx-support.xml",
                "classpath:ru/yandex/metrika/util/common-metrics-support.xml",
                "classpath:ru/yandex/metrika/util/common-monitoring-support.xml",
                "classpath:ru/yandex/metrika/util/juggler-reporter.xml",
                "classpath:ru/yandex/metrika/util/common-jdbc.xml",
                "classpath:ru/yandex/metrika/util/common-tx.xml",
                "classpath:ru/yandex/metrika/util/common-console.xml",
                "classpath:ru/yandex/metrika/rbac/metrika/mobmet-rbac.xml",
                "classpath:ru/yandex/metrika/ch-router-factory.xml",
                "classpath:ru/yandex/metrika/dbclients/clickhouse/clickhouse-log.xml",
                "classpath:ru/yandex/metrika/frontend-common-cache-redis.xml",
                "classpath:ru/yandex/metrika/mobmet/mobmet-common-management.xml",
                "classpath:ru/yandex/metrika/mobmet/push/common/push-common-credentials.xml",
                "classpath:ru/yandex/metrika/mobmet/push/common/push-common-ydb-queue-statlog.xml",
                "classpath:ru/yandex/metrika/frontend-common-security.xml",
                "arcadia_source_file:WEB-INF/push-api.xml",
                "arcadia_source_file:WEB-INF/push-api-jdbc.xml",
                "arcadia_source_file:WEB-INF/push-api-security.xml",
                "arcadia_source_file:WEB-INF/push-api-rbac.xml",
                "arcadia_source_file:WEB-INF/push-api-quota.xml",
                "arcadia_source_file:WEB-INF/push-api-misc.xml",
                "arcadia_source_file:WEB-INF/push-api-servlet.xml",
                "arcadia_source_file:WEB-INF/push-api-ydb.xml"
        },
        reader = ArcadiaSourceAwareBeanDefinitionReader.class
)
public class PushApiConfig {

    @Bean
    public TimeZones timeZones(MySqlJdbcTemplate mobileTemplate) {
        TimeZones timeZones = new TimeZones();
        ApplicationTimeZoneProvider appTimeZoneProvider = new ApplicationTimeZoneProvider(mobileTemplate, timeZones);
        timeZones.setTemplate(mobileTemplate);
        timeZones.setTimeZoneProvider(appTimeZoneProvider);
        timeZones.setUseUtcTimezones(true);
        return timeZones;
    }

    @Bean
    public MtMobGiga mtMobGiga() {
        return () -> {
            throw new UnsupportedOperationException("Test only, needed for mobmet-common-management.xml initialiaztion");
        };
    }
}
