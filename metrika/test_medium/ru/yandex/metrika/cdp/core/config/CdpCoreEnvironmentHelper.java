package ru.yandex.metrika.cdp.core.config;

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

public class CdpCoreEnvironmentHelper extends EnvironmentHelper {

    private static final Logger log = LoggerFactory.getLogger(CdpCoreEnvironmentHelper.class);

    public static String daemonRoot;

    private static String generatedConfigPath;

    private static final CdpCoreSettings settings = new CdpCoreSettings();

    static {
        daemonRoot = inArcadiaTest ? ru.yandex.devtools.test.Paths.getBuildPath("daemon_root") : getPropertyOrDefault("DAEMON_ROOT", "");
    }

    private static Map<String, Object> getParamsMap() {
        return MapBuilder.<String, Object>builder()
                .put("clients_data_table_prefix", ydbDatabase + "/" + settings.getClientsDataTablePrefix())
                .put("schema_data_table_prefix", ydbDatabase + "/" + settings.getSchemaDataTablePrefix())
                .put("cdp_clients_topic", settings.getCdpClientsTopic())
                .put("cdp_clients_consumer", settings.getCdpClientsConsumer())
                .put("cdp_clients_pool_name", settings.getCdpClientsPoolName())
                .put("updated_clients_topic", settings.getUpdateClientsTopic())
                .put("source_id_prefix", settings.getSourceIdPrefix())
                .put("cdp_client_id_change_topic", settings.getCdpClientIdChangeTopic())
                .put("changed_emails_and_phones_topic", settings.getChangedEmailsAndPhonesTopic())
                .put("cdp_orders_topic", settings.getCdpOrdersTopic())
                .put("cdp_orders_consumer", settings.getCdpOrdersConsumer())
                .put("cdp_orders_pool_name", settings.getCdpOrdersPoolName())
                .put("updated_orders_topic", settings.getUpdatedOrdersTopic())
                .put("cdp_events_topic", settings.getCdpEventsTopic())
                .put("cdp_events_consumer", settings.getCdpEventsConsumer())
                .put("cdp_events_pool_name", settings.getCdpEventsPoolName())
                .put("new_events_topic", settings.getNewEventsTopic())
                .put("client_keys_consumer", settings.getClientKeysConsumerPath())
                .put("order_keys_consumer", settings.getOrderKeysConsumerPath())
                .put("changed_emails_consumer", settings.getChangedEmailsAndPhonesConsumerPath())
                .put("cdp_client_id_changes_consumer", settings.getCdpClientIdChangesConsumerPath())
                .put("logbroker_host", logbrokerHost)
                .put("logbroker_port", logbrokerPort)
                .put("ydb_database", ydbDatabase)
                .put("ydb_endpoint", ydbEndpoint)
                .put("clickhouse_host", clickhouseHost)
                .put("clickhouse_port", clickhousePort)
                .put("clickhouse_user", clickhouseUser)
                .put("clickhouse_password", clickhousePassword)
                .put("daemon_root", daemonRoot)
                .build();
    }


    public static void generateConfig() throws IOException {
        var configTemplateContent = IOUtils.resourceAsString(CdpCoreEnvironmentHelper.class, "config_template.xml");
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
