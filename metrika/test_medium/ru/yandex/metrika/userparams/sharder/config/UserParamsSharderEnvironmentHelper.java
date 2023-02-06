package ru.yandex.metrika.userparams.sharder.config;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;
import java.util.Objects;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.util.StringUtil;
import ru.yandex.metrika.util.collections.MapBuilder;
import ru.yandex.metrika.util.io.IOUtils;

public class UserParamsSharderEnvironmentHelper extends EnvironmentHelper {

    private static final Logger log = LoggerFactory.getLogger(EnvironmentHelper.class);

    public static String daemonRoot;

    private static String generatedConfigPath;

    static {
        daemonRoot = inArcadiaTest ? ru.yandex.devtools.test.Paths.getBuildPath("daemon_root") : getPropertyOrDefault("DAEMON_ROOT", "");
    }

    private static Map<String, Object> getParamsMap() {
        return MapBuilder.<String, Object>builder()
                .put("logbroker_host", logbrokerHost)
                .put("logbroker_port", logbrokerPort)
                .put("daemon_root", daemonRoot)
                .put("userparams_updates_topic", UserParamsSharderSettings.getUserparamsUpdatesTopic())
                .put("userparams_sharder_source_id", UserParamsSharderSettings.getUserparamsSharderSourceId())
                .put("userparams_topic", UserParamsSharderSettings.getUserapramsTopic())
                .put("userparams_consumer", UserParamsSharderSettings.getUserparamsConsumer())
                .put("userparams_pool_name", UserParamsSharderSettings.getUserparamsPoolName())
                .build();
    }

    public static void generateConfig() throws IOException {
        var configTemplateContent = IOUtils.resourceAsString(UserParamsSharderEnvironmentHelper.class, "config_template.xml");
        var configContent = StringUtil.substitute(configTemplateContent, getParamsMap());
        log.info("Config content:\n{}", configContent);
        var path = "config.xml";
        Files.writeString(Paths.get(path), configContent);
        generatedConfigPath = path;
    }

    public static String getGeneratedConfigPath() {
        return Objects.requireNonNull(generatedConfigPath, "config was not generated yet");
    }
}
