package ru.yandex.metrika.schedulerd.helpers;

import com.google.common.collect.ImmutableMap;

import ru.yandex.metrika.config.EnvironmentHelper;

public class EnvironmentConfigHelper extends EnvironmentHelper implements ConfigHelper {

    public EnvironmentConfigHelper() {
    }

    @Override
    public void addConfigArgs(ImmutableMap.Builder<String, String> configBuilder) {
        configBuilder
                .put("logbroker_host", logbrokerHost)
                .put("logbroker_port", String.valueOf(logbrokerPort))
//                .put("ydb_database", ydbDatabase)
//                .put("ydb_endpoint", ydbEndpoint)
                .put("mysql_host", mysqlHost)
                .put("mysql_port", String.valueOf(mysqlPort))
                .put("mysql_user", mysqlUser)
                .put("mysql_password", mysqlPassword)
//                .put("mysql_database", mysqlDatabase)
//                .put("postgres_host", postgresHost)
//                .put("postgres_port", String.valueOf(postgresPort))
//                .put("postgres_user", postgresUser)
//                .put("postgres_password", postgresPassword)
//                .put("postgres_database", postgresDatabase)
//                .put("clickhouse_host", clickhouseHost)
//                .put("clickhouse_port", String.valueOf(clickhousePort))
//                .put("clickhouse_user", clickhouseUser)
//                .put("clickhouse_password", clickhousePassword)
        ;
    }
}
