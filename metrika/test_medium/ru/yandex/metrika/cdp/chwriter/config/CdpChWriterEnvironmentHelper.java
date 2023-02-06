package ru.yandex.metrika.cdp.chwriter.config;

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

public class CdpChWriterEnvironmentHelper extends EnvironmentHelper {

    private static final Logger log = LoggerFactory.getLogger(EnvironmentHelper.class);

    public static String daemonRoot;

    private static String generatedConfigPath;

    private static final CdpChWriterSettings settings = new CdpChWriterSettings();

    static {
        daemonRoot = inArcadiaTest ? ru.yandex.devtools.test.Paths.getBuildPath("daemon_root") : getPropertyOrDefault("DAEMON_ROOT", "");
    }

    private static Map<String, Object> getParamsMap() {
        return MapBuilder.<String, Object>builder()
                .put("logbroker_host", logbrokerHost)
                .put("logbroker_port", logbrokerPort)
                .put("ydb_database", ydbDatabase)
                .put("ydb_endpoint", ydbEndpoint)
                .put("orders_pool_name", settings.getOrdersPoolName())
                .put("orders_consumer", settings.getOrdersConsumer())
                .put("orders_topic", settings.getOrdersTopic())
                .put("clients_pool_name", settings.getClientsPoolName())
                .put("clients_consumer", settings.getClientsConsumer())
                .put("clients_topic", settings.getClientsTopic())
                .put("cdp_scheduler_type_matching_changes_source_id_prefix", settings.getCdpSchedulerTypeMatchingChangesSourceIdPrefix())
                .put("cdp_crypta-id_matcher_source_id_prefix", settings.getCdpCryptaIdMatcherSourceIdPrefix())
                .put("cdp_matcher_source_id_prefix", settings.getCdpMatcherSourceIdPrefix())
                .put("cdp_core_source_id_prefix", settings.getCdpCoreSourceIdPrefix())
                .put("matching_data_tables_prefix", ydbDatabase + "/" + settings.getMatchingDataTablesPrefix())
                .put("meta_data_tables_prefix", ydbDatabase + "/" + settings.getMetaDataTablesPrefix())
                .put("clients_data_table_prefix", ydbDatabase + "/" + settings.getClientsDataTablePrefix())
                .put("clickhouse_host", clickhouseHost)
                .put("clickhouse_port", clickhousePort)
                .put("clickhouse_user", clickhouseUser)
                .put("clickhouse_password", clickhousePassword)
                .put("daemon_root", daemonRoot)
                .build();
    }

    public static void generateConfig() throws IOException {
        var configTemplateContent = IOUtils.resourceAsString(CdpChWriterEnvironmentHelper.class, "config_template.xml");
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
