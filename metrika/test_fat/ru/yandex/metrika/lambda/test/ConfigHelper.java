package ru.yandex.metrika.lambda.test;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

import com.google.common.collect.ImmutableMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.util.app.XmlPropertyConfigurer;

import static ru.yandex.devtools.test.Paths.getBuildPath;
import static ru.yandex.metrika.lambda.steps.FreemarkerUtils.renderTemplate;

public final class ConfigHelper {

    private static final Logger log = LoggerFactory.getLogger(ConfigHelper.class);

    private ConfigHelper() {}

    public static void configure() {
        final String configFile = getBuildPath("config.xml");
        ImmutableMap.Builder<String, String> overrideEnvBuilder = ImmutableMap.builder();
        overrideEnvBuilder.put("targetHost", "localhost");

        log.info("Сonfiguratin file: {}", configFile);

        try (BufferedWriter writer = Files.newBufferedWriter(Paths.get(configFile))) {
            writer.write(renderTemplate("test/config.conf.ftl", ImmutableMap.<String, String>builder()
                    .putAll(System.getenv())
                    .putAll(overrideEnvBuilder.build())
                    .put("daemonRoot", getBuildPath("opt/yandex/lambda-visits"))
                    .put("ytRpcProxyPort", System.getenv("YT_RPC_PROXY").split(":")[1])
                    .put("ytProxyPort", System.getenv("YT_PROXY").split(":")[1])
                    .put("yqlHost", System.getenv("YQL_HOST"))
                    .put("yqlPort", System.getenv("YQL_PORT"))
                    .put("yqlDatabase", System.getenv("YQL_DB"))
                    .build()));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        System.setProperty(XmlPropertyConfigurer.RESOURCE_KEY, configFile);
        System.setProperty("jmxDefaultDomain", LambdaTest.class.getName());
    }
}
