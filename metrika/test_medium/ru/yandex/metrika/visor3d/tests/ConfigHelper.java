package ru.yandex.metrika.visor3d.tests;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

import com.google.common.collect.ImmutableMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.visor3d.steps.Visor3dSettings;

import static java.lang.String.valueOf;
import static org.springframework.util.SocketUtils.findAvailableTcpPort;
import static ru.yandex.devtools.test.Paths.getBuildPath;
import static ru.yandex.metrika.common.test.medium.FreemarkerUtils.renderTemplate;

public final class ConfigHelper {

    private static final Logger log = LoggerFactory.getLogger(ConfigHelper.class);

    private static Visor3dSettings settings = new Visor3dSettings();

    private ConfigHelper() {
    }

    public static void configure() {
        final String configFile = getBuildPath("config.xml");
        ImmutableMap.Builder<String, String> overrideEnvBuilder = ImmutableMap.builder();
        overrideEnvBuilder.put("targetHost", "localhost");

        log.info("Сonfiguratin file: {}", configFile);

        try (BufferedWriter writer = Files.newBufferedWriter(Paths.get(configFile))) {
            writer.write(renderTemplate("/ru/yandex/metrika/visor3d", "tests/config.conf.ftl", ImmutableMap.<String, String>builder()
                    .putAll(System.getenv())
                    .putAll(overrideEnvBuilder.build())
                    .put("jmxPort", valueOf(findAvailableTcpPort()))
                    .put("queuesRootPath", settings.getQueuesRoot())
                    .put("inputQueuesSuffix", settings.getInputQueuesSuffix())
                    .put("outputQueuesPath", settings.getOutputQueuesPath())
                    .put("ytPathPrefix", settings.getYtPathPrefix())
                    .put("logbrokerEventsTopic", settings.getLogbrokerEventsTopic())
                    .put("logbrokerStaticTopic", settings.getLogbrokerStaticTopic())
                    .put("logbrokerCryptaTopic", settings.getLogbrokerCryptaTopic())
                    .put("logbrokerScrollsTopic", settings.getLogbrokerScrollsTopic())
                    .put("logbrokerFormsTopic", settings.getLogbrokerFormsTopic())
                    .put("logbrokerWvSourceTopic", settings.getLogbrokerSourceWvLogTopic())
                    .put("logbrokerWvAppendSasTopic", settings.getLogbrokerSourceWvLogTopic())
                    .put("logbrokerWvAppendVlaTopic", settings.getLogbrokerSourceWvLogTopic())
                    .build()));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        System.setProperty(XmlPropertyConfigurer.RESOURCE_KEY, configFile);
        System.setProperty("jmxDefaultDomain", Visor3dBaseTest.class.getName());
    }

}
