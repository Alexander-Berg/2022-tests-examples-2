package ru.yandex.metrika.userparams2d.config;

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

import static java.lang.String.valueOf;
import static org.springframework.util.SocketUtils.findAvailableTcpPort;

public class UserParamsEnvironmentHelper extends EnvironmentHelper {

    private static final Logger log = LoggerFactory.getLogger(UserParamsEnvironmentHelper.class);

    private static final UserParamsSettings settings = new UserParamsSettings();

    public static String daemonRoot;

    private static String generatedConfigPath;

    static {
        daemonRoot = inArcadiaTest ? ru.yandex.devtools.test.Paths.getBuildPath("daemon_root") : getPropertyOrDefault("DAEMON_ROOT", "");
    }

    private static Map<String, Object> getParamsMap() {
        return MapBuilder.<String, Object>builder()
                .put("logbroker_host", logbrokerHost)
                .put("logbroker_port", logbrokerPort)
                .put("recipe_mysql_host", mysqlHost)
                .put("recipe_mysql_port", mysqlPort)
                .put("recipe_mysql_user", mysqlUser)
                .put("recipe_clickhouse_host", clickhouseHost)
                .put("recipe_clickhouse_http_port", clickhousePort)
                .put("recipe_counters_server_port", System.getenv("RECIPE_COUNTERS_SERVER_PORT"))
                .put("yt_proxy_port", System.getenv("YT_PROXY").split(":")[1])
                .put("target_host", "localhost")
                .put("recipe_zookeeper_host", System.getenv("RECIPE_ZOOKEEPER_HOST"))
                .put("recipe_zookeeper_port", System.getenv("RECIPE_ZOOKEEPER_PORT"))
                .put("s3mds_port", System.getenv("S3MDS_PORT"))
                .put("daemon_root", daemonRoot)
                .put("jmx_port", valueOf(findAvailableTcpPort()))
                .put("yt_path_prefix", settings.getYtPathPrefix())
                .put("userparams_giga_topic", settings.getUserparamsGigaTopic())
                .put("userparams_nano_topic", settings.getUserparamsNanoTopic())
                .put("userparams_updates_topic",settings.getUserparamUpdatesTopic())
                .put("userparams_updates_consumer", settings.getUserparamsUpdatesConsumerPath())
                .put("core_source_id", settings.getCoreSourceId())
                .build();
    }

    public static void generateConfig() throws IOException {
        var configTemplateContent = IOUtils.resourceAsString(UserParamsEnvironmentHelper.class, "config_template.xml");
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
