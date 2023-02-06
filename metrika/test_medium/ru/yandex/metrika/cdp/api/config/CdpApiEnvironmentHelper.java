package ru.yandex.metrika.cdp.api.config;

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

public class CdpApiEnvironmentHelper extends EnvironmentHelper {

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
                .put("ydb_database", ydbDatabase)
                .put("ydb_endpoint", ydbEndpoint)
                .put("mysql_host", mysqlHost)
                .put("mysql_port", mysqlPort)
                .put("mysql_user", mysqlUser)
                .put("mysql_password", mysqlPassword)
                .put("mysql_database", mysqlDatabase)
                .put("postgres_host", postgresHost)
                .put("postgres_port", postgresPort)
                .put("postgres_user", postgresUser)
                .put("postgres_password", postgresPassword)
                .put("postgres_database", postgresDatabase)
                .put("clickhouse_host", clickhouseHost)
                .put("clickhouse_port", clickhousePort)
                .put("clickhouse_user", clickhouseUser)
                .put("clickhouse_password", clickhousePassword)
                .put("daemon_root", daemonRoot)
                .build();
    }

    public static void generateConfig() throws IOException {
        var configTemplateContent = IOUtils.resourceAsString(CdpApiEnvironmentHelper.class, "config_template.xml");
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
