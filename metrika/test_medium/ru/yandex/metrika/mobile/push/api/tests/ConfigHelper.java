package ru.yandex.metrika.mobile.push.api.tests;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;

import com.google.common.collect.ImmutableMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.common.test.medium.MediumTestsLogSetup;
import ru.yandex.metrika.dbclients.MdsSetupUtils;
import ru.yandex.metrika.dbclients.config.MdsTestConfig;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;

import static java.lang.String.valueOf;
import static org.springframework.util.SocketUtils.findAvailableTcpPort;
import static ru.yandex.devtools.test.Paths.getBuildPath;
import static ru.yandex.metrika.common.test.medium.FreemarkerUtils.renderTemplate;

public final class ConfigHelper {

    private static final Logger log = LoggerFactory.getLogger(ConfigHelper.class);

    private static volatile boolean initialized = false;

    private ConfigHelper() {
    }

    public static synchronized void configure() {
        if (initialized) {
            return;
        }

        configureLogger();
        setupS3();
        writeConfig();

        initialized = true;
    }

    private static void configureLogger() {
        MediumTestsLogSetup.setup();
    }

    private static void setupS3() {
        MdsTestConfig config = MdsSetupUtils.arcadiaConfig();
        MdsSetupUtils.createBucket(config, "appmetrica-push");
    }

    private static void writeConfig() {
        String configFile = getBuildPath("config.xml");
        ImmutableMap.Builder<String, String> overrideEnvBuilder = ImmutableMap.builder();
        overrideEnvBuilder.put("targetHost", "localhost");

        log.info("Сonfiguration file: {}", configFile);

        Map<String, String> parameters = ImmutableMap.<String, String>builder()
                .putAll(System.getenv())
                .putAll(overrideEnvBuilder.build())
                .putAll(MdsSetupUtils.arcadiaConfig().asFtlParams())
                .put("daemonRoot", getBuildPath("opt/yandex/push-api"))
                .put("apiPort", valueOf(findAvailableTcpPort()))
                .build();
        try (BufferedWriter writer = Files.newBufferedWriter(Paths.get(configFile))) {
            writer.write(renderTemplate("/ru/yandex/metrika/mobile/push/api", "tests/config.conf.ftl", parameters));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        System.setProperty(XmlPropertyConfigurer.RESOURCE_KEY, configFile);
        System.setProperty("jmxDefaultDomain", PushApiBaseTest.class.getName());
    }
}
