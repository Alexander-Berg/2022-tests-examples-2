package ru.yandex.metrika.cdp.core.tests.medium;

import java.io.IOException;

import org.apache.logging.log4j.Level;
import org.junit.BeforeClass;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.cdp.core.config.CdpCoreEnvironmentHelper;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.util.app.DaemonName;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.log.Log4jSetup;

public class CdpCoreTestSetup {
    private static final Logger log = LoggerFactory.getLogger(CdpCoreTestSetup.class);
    private static volatile boolean setupDone = false;

    @BeforeClass
    public static void setup() throws IOException {
        if (!setupDone) {
            synchronized (CdpCoreTestSetup.class) {
                if (!setupDone) {
                    setupLogging();

                    setupConfig();

                    setupSystemProperties();

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
        CdpCoreEnvironmentHelper.generateConfig();
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
        System.setProperty(XmlPropertyConfigurer.RESOURCE_KEY, CdpCoreEnvironmentHelper.getGeneratedConfigPath());
        System.setProperty(DaemonName.PROP_NAME, "cdp-core-test");
        System.setProperty("jmxDefaultDomain", "cdp-core-test");
    }

    //todo
    private static void setupYdb() {
        log.info("Setting up YDB");
        YdbSetupUtil.setupYdbFolders("schema", "clients_data");
    }
}
