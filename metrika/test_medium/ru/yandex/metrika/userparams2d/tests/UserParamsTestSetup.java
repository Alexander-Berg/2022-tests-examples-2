package ru.yandex.metrika.userparams2d.tests;

import java.io.IOException;
import java.util.stream.Stream;

import org.apache.logging.log4j.Level;
import org.junit.BeforeClass;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;

import ru.yandex.clickhouse.ClickHouseDataSource;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.TestSetupHelper;
import ru.yandex.metrika.userparams2d.config.UserParamsEnvironmentHelper;
import ru.yandex.metrika.util.app.DaemonName;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.log.Log4jSetup;

public class UserParamsTestSetup {

    private static final Logger log = LoggerFactory.getLogger(UserParamsEnvironmentHelper.class);
    private static volatile boolean setupDone = false;

    @BeforeClass
    public static void setup() throws IOException {
        if (!setupDone) {
            synchronized (UserParamsTestSetup.class) {
                if (!setupDone) {
                    setupLogging();

                    setupConfig();

                    setupSystemProperties();

                    setupClickhouse();

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
        Log4jSetup.basicArcadiaSetup(Level.ALL);
        Log4jSetup.mute("com.atomikos.jdbc");
        Log4jSetup.mute("ru.yandex.metrika.util.chunk.clickhouse.haze.FreeSpaceBasedNodeWeighProvider");
        Log4jSetup.mute("ru.yandex.misc.io.http.apache.v4.ApacheHttpClient4Utils");
        Log4jSetup.mute("ru.yandex.yt.ytclient.bus");
        Log4jSetup.mute("ru.yandex.yt.ytclient.proxy.ApiServiceClient");
        Log4jSetup.mute("ru.yandex.yt.ytclient.proxy.PeriodicDiscovery");
        Log4jSetup.mute("ru.yandex.yt.ytclient.rpc");
//        Log4jSetup.mute("ru.yandex.commune.zk2");
//        Log4jSetup.mute("org.apache.zookeeper");
//        Log4jSetup.mute("ru.yandex.commune.bazinga");
    }

    private static void setupConfig() throws IOException {
        log.info("Setting up config");
        UserParamsEnvironmentHelper.generateConfig();
    }

    private static void setupSystemProperties() {
        log.info("Setting up system properties");
        System.setProperty(XmlPropertyConfigurer.RESOURCE_KEY, UserParamsEnvironmentHelper.getGeneratedConfigPath());
        System.setProperty(DaemonName.PROP_NAME, "userparams2d-test");
        System.setProperty("jmxDefaultDomain", "userparams2d-test");
    }

    private static void setupClickhouse() {
        log.info("setting up clickhouse");
        var clickHouseDataSource = new ClickHouseDataSource("jdbc:clickhouse://" + EnvironmentHelper.clickhouseHost + ":" + EnvironmentHelper.clickhousePort);

        TestSetupHelper.populateDB(
                clickHouseDataSource,
                Stream.of("00_userparams_schema.sql")
                        .map(s -> new ClassPathResource("../clickhouse/" + s, UserParamsTestSetup.class))
                        .toArray(Resource[]::new)
        );
    }
}
