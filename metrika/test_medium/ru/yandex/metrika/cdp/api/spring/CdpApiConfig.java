package ru.yandex.metrika.cdp.api.spring;

import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ImportResource;

import ru.yandex.metrika.config.ArcadiaSourceAwareBeanDefinitionReader;

/**
 * Класс реализующий полную конфигурацию cdp-api
 */
@SuppressWarnings("SpringImportResource")
@Configuration
@ImportResource(
        locations = {
                "classpath:/ru/yandex/metrika/cdp/mtcdp-router-config.xml",
                "classpath:/ru/yandex/metrika/cdp/segments/cdp-segments.xml",
                "classpath:/ru/yandex/metrika/util/common-jdbc.xml",
                "classpath:/ru/yandex/metrika/cdp/frontend/cdp-frontend-common.xml",
                "classpath:/ru/yandex/metrika/util/common-jmx-support.xml",
                "classpath:/ru/yandex/metrika/util/common-metrics-support.xml",
                "classpath:/ru/yandex/metrika/util/common-monitoring-support.xml",
                "classpath:/ru/yandex/metrika/frontend-common-quota-redis.xml",
                "classpath:/ru/yandex/metrika/common-security.xml",
                "classpath:/ru/yandex/metrika/rbac/metrika/metrika-rbac.xml",
                "classpath:/ru/yandex/metrika/frontend-common-security.xml",
                "classpath:/ru/yandex/metrika/frontend-common.xml",
                "classpath:/ru/yandex/metrika/frontend-common-cache-redis.xml",
                "classpath:/ru/yandex/metrika/frontend-common-ch.xml",
                "classpath:/ru/yandex/metrika/frontend-common-stubbed-yt-dicts-dao.xml",
                "classpath:/ru/yandex/metrika/frontend-common-jdbc.xml",
                "classpath:/ru/yandex/metrika/counters-flags.xml",
                "classpath:/ru/yandex/metrika/api/management/spring/test-counter-creator-config.xml",
                "classpath:/ru/yandex/metrika/dbclients/clickhouse/clickhouse-log.xml",
                "classpath:/ru/yandex/metrika/mtgiga-router-config.xml",
                "classpath:/ru/yandex/metrika/mtnano-router-config.xml",
                "classpath:/ru/yandex/metrika/mtaggr-router-config.xml",
                "arcadia_source_file:webapp/WEB-INF/cdp-api.xml",
                "arcadia_source_file:webapp/WEB-INF/cdp-api-security.xml",
                "arcadia_source_file:webapp/WEB-INF/cdp-api-servlet.xml",
                "arcadia_source_file:webapp/WEB-INF/cdp-api-logbroker.xml"
        },
        reader = ArcadiaSourceAwareBeanDefinitionReader.class
)
public class CdpApiConfig {
}
