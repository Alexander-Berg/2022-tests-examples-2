package ru.yandex.metrika.cdp.chwriter.tests.medium;

import java.io.IOException;
import java.util.stream.Stream;

import org.apache.logging.log4j.Level;
import org.junit.BeforeClass;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;

import ru.yandex.clickhouse.ClickHouseDataSource;
import ru.yandex.metrika.cdp.chwriter.config.CdpChWriterEnvironmentHelper;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.TestSetupHelper;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.util.app.DaemonName;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.log.Log4jSetup;


public class CdpChWriterTestSetup {
    private static final Logger log = LoggerFactory.getLogger(CdpChWriterTestSetup.class);
    private static volatile boolean setupDone = false;

    @BeforeClass
    public static void setup() throws IOException {
        if (!setupDone) {
            synchronized (CdpChWriterTestSetup.class) {
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

    private static void setupConfig() throws IOException {
        log.info("Setting up config");
        CdpChWriterEnvironmentHelper.generateConfig();
    }

    private static void setupLogging() {
        Log4jSetup.basicArcadiaSetup(Level.ALL);
        Log4jSetup.mute("ru.yandex.misc.io.http.apache.v4.ApacheHttpClient4Utils");
        Log4jSetup.mute("ru.yandex.yt.ytclient.bus");
        Log4jSetup.mute("ru.yandex.yt.ytclient.proxy.ApiServiceClient");
        Log4jSetup.mute("ru.yandex.yt.ytclient.proxy.PeriodicDiscovery");
        Log4jSetup.mute("ru.yandex.yt.ytclient.rpc");
    }

    private static void setupSystemProperties() {
        log.info("Setting up system properties");
        System.setProperty(XmlPropertyConfigurer.RESOURCE_KEY, CdpChWriterEnvironmentHelper.getGeneratedConfigPath());
        System.setProperty(DaemonName.PROP_NAME, "cdp-ch-writer-test");
        System.setProperty("jmxDefaultDomain", "cdp-ch-writer-test");
    }

    private static void setupClickhouse() {
        log.info("setting up clickhouse");
        var clickHouseDataSource = new ClickHouseDataSource("jdbc:clickhouse://" + EnvironmentHelper.clickhouseHost + ":" + EnvironmentHelper.clickhousePort);

        TestSetupHelper.populateDB(
                clickHouseDataSource,
                Stream.of("clients_schema.sql", "orders_schema.sql")
                        .map(s -> new ClassPathResource("../../clickhouse/" + s, CdpChWriterTestSetup.class))
                        .toArray(Resource[]::new)
        );
    }

    private static void setupYdb() {
        log.info("Setting up YDB");
        YdbSetupUtil.setupYdbFolders("schema", "clients_data", "ch_writer_meta", "matching");
    }
}
