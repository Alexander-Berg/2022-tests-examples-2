package ru.yandex.metrika.cdp.api.tests.medium;

import java.io.IOException;
import java.util.Map;
import java.util.stream.Stream;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.security.util.InMemoryResource;

import ru.yandex.clickhouse.ClickHouseDataSource;
import ru.yandex.metrika.cdp.api.config.CdpApiEnvironmentHelper;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.TestSetupHelper;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.util.StringUtil;
import ru.yandex.metrika.util.app.DaemonName;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.io.IOUtils;
import ru.yandex.metrika.util.log.Log4jSetup;

public class CdpApiTestSetup {

    private static final Logger log = LoggerFactory.getLogger(CdpApiTestSetup.class);
    private static volatile boolean setupDone = false;


    public static void globalSetup() throws Exception {
        if (!setupDone) {
            synchronized (CdpApiTestSetup.class) {
                if (!setupDone) {
                    setupLogging();

                    setupConfig();

                    setupSystemProperties();

                    setupClickhouse();

                    setupYdb();

                    setupDone = true;
                } else {
                    log.info("Setup already had been performed earlier");
                }
            }
        } else {
            log.info("Setup already had been performed earlier");
        }
    }

    private static void setupLogging() {
        log.info("Setting up logging");
        Log4jSetup.mute("ru.yandex.yt.ytclient.rpc");
        Log4jSetup.mute("ru.yandex.yt.ytclient.bus");
        Log4jSetup.mute("ru.yandex.misc.io.http.apache.v4.ApacheHttpClient4Utils");
        Log4jSetup.mute("ru.yandex.yt.ytclient.proxy.ApiServiceClient");
        Log4jSetup.mute("ru.yandex.yt.ytclient.proxy.PeriodicDiscovery");
        Log4jSetup.mute("com.codahale.metrics.graphite.GraphiteReporter");
        Log4jSetup.mute("com.netflix.servo.publish.graphite.GraphiteMetricObserver");
    }

    private static void setupConfig() throws IOException {
        log.info("Setting up config");
        CdpApiEnvironmentHelper.generateConfig();
    }

    private static void setupSystemProperties() {
        log.info("Setting up system properties");
        System.setProperty(XmlPropertyConfigurer.RESOURCE_KEY, CdpApiEnvironmentHelper.getGeneratedConfigPath());
        System.setProperty(DaemonName.PROP_NAME, "cdp-api-test");
        System.setProperty("jmxDefaultDomain", "cdp-api-test");
    }

    private static void setupClickhouse() {
        log.info("setting up clickhouse");
        var clickHouseDataSource = new ClickHouseDataSource("jdbc:clickhouse://" + EnvironmentHelper.clickhouseHost + ":" + EnvironmentHelper.clickhousePort);

        TestSetupHelper.populateDB(
                clickHouseDataSource,
                Stream.of("00_cdp_schema.sql")
                        .map(s -> new ClassPathResource("../../clickhouse/" + s, CdpApiTestSetup.class))
                        .toArray(Resource[]::new)
        );
    }

    private static void setupYdb() {
        log.info("Setting up YDB");
        YdbSetupUtil.setupYdbFolders("schema", "segments_data", "system_data", "clients_data");
    }

    public static void prepareClickhouse(Map<String, Object> templateParams) {
        var templateContent = IOUtils.resourceAsString(CdpApiTestSetup.class, "../../clickhouse/99_cdp_clients_data_template.sql");
        var script = StringUtil.substitute(templateContent, templateParams);
        var clickHouseDataSource = new ClickHouseDataSource("jdbc:clickhouse://" + EnvironmentHelper.clickhouseHost + ":" + EnvironmentHelper.clickhousePort);

        TestSetupHelper.populateDB(clickHouseDataSource, new InMemoryResource(script));
    }
}
