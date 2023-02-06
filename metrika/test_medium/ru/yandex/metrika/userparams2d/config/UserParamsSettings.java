package ru.yandex.metrika.userparams2d.config;

import org.springframework.stereotype.Component;

import ru.yandex.yt.ytclient.tables.TableSchema;

import static java.lang.String.format;
import static ru.yandex.metrika.userparams.YtParamsTableMeta.CLIENT_USER_ID_MATCHING_TABLE_SCHEMA;
import static ru.yandex.metrika.userparams.YtParamsTableMeta.PARAMS_TABLE_SCHEMA;
import static ru.yandex.metrika.userparams.YtParamsTableMeta.PARAM_OWNERS_TABLE_SCHEMA;

@Component
public class UserParamsSettings {

    private final String ytPathPrefix = "//home";

    private final String paramOwnersYtTable = format("%s/param_owners", ytPathPrefix);

    private final String clientUserIdMatchingYtTable = format("%s/client_user_id_matching", ytPathPrefix);

    private final String paramsYtTable = format("%s/params", ytPathPrefix);

    private final String userparamUpdatesTopic = "userparams-sharded-log";

    private final String userparamsGigaTopic = "userparams-giga-log";

    private final String userparamsNanoTopic = "userparams-nano-log";

    private final String userparamsUpdatesConsumerPath = "userparams-sharded-log-consumer";

    private final String coreSourceId = "userparams-sharder";

    private final String apiSourceId = "userparams-api";

    private final String gigaLogConsumer = "giga-log-consumer";

    private final String nanoLogConsumer = "nano-log-consumer";

    private static final TableSchema paramsTableSchema = PARAMS_TABLE_SCHEMA;

    private final TableSchema paramOwnersTableSchema = PARAM_OWNERS_TABLE_SCHEMA;

    private final TableSchema paramOwnersWithClientUseIdTableSchema = CLIENT_USER_ID_MATCHING_TABLE_SCHEMA;

    public String getYtPathPrefix() {
        return ytPathPrefix;
    }

    public String getParamOwnersYtTable() {
        return paramOwnersYtTable;
    }

    public String getParamsYtTable() {
        return paramsYtTable;
    }

    public String getUserparamsGigaTopic() {
        return userparamsGigaTopic;
    }

    public String getUserparamsNanoTopic() {
        return userparamsNanoTopic;
    }

    public TableSchema getParamsTableSchema() {
        return paramsTableSchema;
    }

    public TableSchema getParamOwnersTableSchema() {
        return paramOwnersTableSchema;
    }

    public String getUserparamUpdatesTopic() {
        return userparamUpdatesTopic;
    }

    public String getClientUserIdMatchingYtTable() {
        return clientUserIdMatchingYtTable;
    }


    public String getUserparamsUpdatesConsumerPath() {
        return userparamsUpdatesConsumerPath;
    }

    public TableSchema getParamOwnersWithClientUseIdTableSchema() {
        return paramOwnersWithClientUseIdTableSchema;
    }

    public String getCoreSourceId() {
        return coreSourceId;
    }

    public String getApiSourceId() {
        return apiSourceId;
    }

    public String getGigaLogConsumer() {
        return gigaLogConsumer;
    }

    public String getNanoLogConsumer() {
        return nanoLogConsumer;
    }
}
