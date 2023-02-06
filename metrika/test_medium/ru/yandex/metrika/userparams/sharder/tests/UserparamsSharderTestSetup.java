package ru.yandex.metrika.userparams.sharder.tests;

import java.io.IOException;

import org.junit.BeforeClass;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.userparams.sharder.config.UserParamsSharderEnvironmentHelper;
import ru.yandex.metrika.util.app.DaemonName;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;


public class UserparamsSharderTestSetup {

    private static final Logger log = LoggerFactory.getLogger(UserParamsSharderEnvironmentHelper.class);
    private static volatile boolean setupDone = false;

    @BeforeClass
    public static void setup() throws IOException {
        if (!setupDone) {
            synchronized (UserparamsSharderTestSetup.class) {
                if (!setupDone) {
                    setupConfig();

                    setupSystemProperties();

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
        UserParamsSharderEnvironmentHelper.generateConfig();
    }

    private static void setupSystemProperties() {
        log.info("Setting up system properties");
        System.setProperty(XmlPropertyConfigurer.RESOURCE_KEY, UserParamsSharderEnvironmentHelper.getGeneratedConfigPath());
        System.setProperty(DaemonName.PROP_NAME, "userparams-sharder-test");
        System.setProperty("jmxDefaultDomain", "userparams-sharder-test");
    }
}
