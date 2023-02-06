package ru.yandex.metrika.config;

import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;

import org.apache.commons.lang3.tuple.Pair;
import org.apache.logging.log4j.Level;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.log.Log4jSetup;

import static java.util.stream.Collectors.joining;
import static org.apache.commons.lang3.StringUtils.prependIfMissing;

public class EnvironmentHelper {

    static {
        Log4jSetup.basicArcadiaSetup(Level.INFO);
    }

    private static final Logger log = LoggerFactory.getLogger(EnvironmentHelper.class);
    private static final String LOCALHOST = "localhost";
    private static final Map<String, String> allProperties = new HashMap<>();


    public static final boolean inArcadiaTest;
    public static final String defaultHost;

    public static final String logbrokerHost;
    public static final int logbrokerPort;

    public static final String ydbEndpoint;
    public static final String ydbDatabase;

    public static final String mysqlHost;
    public static final int mysqlPort;
    public static final String mysqlUser;
    public static final String mysqlPassword;
    public static final String mysqlDatabase;

    public static final boolean allowMysqlPopulationSkip;

    public static final String postgresHost;
    public static final int postgresPort;
    public static final String postgresUser;
    public static final String postgresPassword;
    public static final String postgresDatabase;

    public static final String clickhouseHost;
    public static final int clickhousePort;
    public static final String clickhouseUser;
    public static final String clickhousePassword;

    public static final String ytProxy;

    protected static String getPropertyOrDefault(String key, String def) {
        return allProperties.getOrDefault(key, def);
    }

    protected static int getPropertyOrDefaultInt(String key, int def) {
        return Optional.ofNullable(allProperties.get(key)).map(Integer::valueOf).orElse(def);
    }

    protected static boolean getPropertyOrDefaultBoolean(String key, boolean def) {
        return Optional.ofNullable(allProperties.get(key)).map(Boolean::valueOf).orElse(def);
    }

    protected static void logPropsMap(Map<String, String> props, String message) {
        log.info(message + ":\n{}", props.entrySet().stream().map(F.mapEntity((key, value) -> key + "=" + value)).sorted().collect(joining("\n")));
    }

    private static Map<String, String> loadDefaultProperties() {
        if (inArcadiaTest) {
            return Map.of();
        }

        var defaultPropertiesFile = Paths.get(
                System.getProperty("user.home"),
                ".metrika", "tests", "default.properties"
        ).toFile();


        if (defaultPropertiesFile.exists() && defaultPropertiesFile.canRead()) {
            try {
                var properties = new Properties();
                properties.load(new FileReader(defaultPropertiesFile));
                var result = properties.entrySet().stream()
                        .map(F.mapEntity((key, value) -> Pair.of(key.toString(), value.toString())))
                        .collect(F.pairToMapCollector());
                logPropsMap(result, "Load properties");
                return result;
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }

        log.info(
                "Can not read default properties file. Path: {}, exists: {}, can read: {}",
                defaultPropertiesFile.toPath().toAbsolutePath(),
                defaultPropertiesFile.exists(),
                defaultPropertiesFile.canRead()
        );
        return Map.of();
    }

    static {
        log.info("Current path: {}", Paths.get(".").toAbsolutePath());
        inArcadiaTest = ru.yandex.devtools.test.Paths.getTestOutputsRoot() != null;
        log.warn("In arcadia test: {}", inArcadiaTest);
        var envVars = System.getenv();
        logPropsMap(envVars, "Env vars map");
        var defaultProperties = loadDefaultProperties();

        envVars.forEach(allProperties::putIfAbsent);
        defaultProperties.forEach(allProperties::putIfAbsent);

        logPropsMap(allProperties, "All properties");

        defaultHost = inArcadiaTest ? LOCALHOST : getPropertyOrDefault("DEFAULT_HOST", LOCALHOST);

        logbrokerHost = inArcadiaTest ? LOCALHOST : getPropertyOrDefault("LOGBROKER_HOST", defaultHost);
        logbrokerPort = getPropertyOrDefaultInt("LOGBROKER_PORT", 2136);

        ydbEndpoint = getPropertyOrDefault("YDB_ENDPOINT", defaultHost + ":2135");
        ydbDatabase = prependIfMissing(getPropertyOrDefault("YDB_DATABASE", "local"), "/");

        mysqlHost = getPropertyOrDefault("RECIPE_MYSQL_HOST", defaultHost);
        mysqlPort = getPropertyOrDefaultInt("RECIPE_MYSQL_PORT", 3306);
        mysqlUser = getPropertyOrDefault("RECIPE_MYSQL_USER", "root");
        mysqlPassword = getPropertyOrDefault("RECIPE_MYSQL_PASSWORD", "root");
        mysqlDatabase = getPropertyOrDefault("RECIPE_MYSQL_DATABASE", "");

        allowMysqlPopulationSkip = !inArcadiaTest && getPropertyOrDefaultBoolean("ALLOW_MYSQL_POPULATION_SKIP", true);

        postgresHost = getPropertyOrDefault("POSTGRES_RECIPE_HOST", defaultHost);
        postgresPort = getPropertyOrDefaultInt("POSTGRES_RECIPE_PORT", 5432);
        postgresUser = getPropertyOrDefault("POSTGRES_RECIPE_USER", "");
        postgresPassword = getPropertyOrDefault("POSTGRES_RECIPE_PASSWORD", "");
        postgresDatabase = getPropertyOrDefault("POSTGRES_RECIPE_DBNAME", "");

        clickhouseHost = getPropertyOrDefault("RECIPE_CLICKHOUSE_HOST", defaultHost);
        clickhousePort = getPropertyOrDefaultInt("RECIPE_CLICKHOUSE_HTTP_PORT", 8123);
        clickhouseUser = getPropertyOrDefault("RECIPE_CLICKHOUSE_USER", "default");
        clickhousePassword = getPropertyOrDefault("RECIPE_CLICKHOUSE_PASSWORD", "");

        ytProxy = getPropertyOrDefault("YT_PROXY", defaultHost + ":8000");
    }
}
