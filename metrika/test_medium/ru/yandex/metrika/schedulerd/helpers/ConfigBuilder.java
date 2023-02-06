package ru.yandex.metrika.schedulerd.helpers;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;

import com.google.common.collect.ImmutableMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.util.app.XmlPropertyConfigurer;

import static ru.yandex.devtools.test.Paths.getBuildPath;
import static ru.yandex.metrika.common.test.medium.FreemarkerUtils.renderTemplate;

public class ConfigBuilder {

    private static final String CONFIG_FILE = "config.xml";
    private static final Logger log = LoggerFactory.getLogger(ConfigBuilder.class);
    private final List<ConfigHelper> helperList;
    private final String className; // = "/ru/yandex/metrika/schedulerd"
    private final String rootConfig; // = "config/config.conf.ftl";
    private final String targetHost; // = "localhost"

    public ConfigBuilder(List<ConfigHelper> helperList, String className, String rootConfig, String targetHost) {
        this.helperList = helperList;
        this.className = className;
        this.rootConfig = rootConfig;
        this.targetHost = targetHost;
    }

    public ConfigBuilder(List<ConfigHelper> helperList, String className) {
        this(helperList, className, "config/config.conf.ftl", "localhost");
    }

    public ConfigBuilder(List<ConfigHelper> helperList, String className, String targetHost) {
        this(helperList, className, "config/config.conf.ftl", targetHost);
    }

    public void configure() {
        String configPath = getBuildPath(CONFIG_FILE);
        if (configPath.startsWith("null")) {
            configPath = configPath.replaceFirst("null/", "/tmp/");
        }
        log.info("Configuration file: {}", configPath);

        // Сбор основных параметров рендеринга шаблона конфигурации
        ImmutableMap.Builder<String, String> configBuilder = ImmutableMap.builder();
        configBuilder.put("targetHost", targetHost);
        helperList.forEach(configHelper -> configHelper.addConfigArgs(configBuilder));
        Map<String, String> config = configBuilder.build();
        log.debug(config.toString());

        try (BufferedWriter writer = Files.newBufferedWriter(Paths.get(configPath))) {
            String conf = renderTemplate(className, rootConfig, config);
            log.debug(String.format("Generated: \n %s", conf));
            writer.write(conf);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        // Действия необходимые перед запуском
        System.setProperty(XmlPropertyConfigurer.RESOURCE_KEY, configPath);
        helperList.forEach(ConfigHelper::apply);
    }
}
