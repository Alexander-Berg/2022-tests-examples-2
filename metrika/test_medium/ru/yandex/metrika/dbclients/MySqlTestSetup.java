package ru.yandex.metrika.dbclients;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.config.ResourceHelper;
import ru.yandex.metrika.dbclients.mysql.DataSourceFactory;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.mysql.RowMappers;
import ru.yandex.metrika.dbclients.mysql.TransactionalMetrikaDataSource;

public class MySqlTestSetup {

    private static final Logger log = LoggerFactory.getLogger(MySqlTestSetup.class);
    private static volatile boolean setupDone = false;

    public static void globalSetup() throws Exception {
        if (!setupDone) {
            synchronized (MySqlTestSetup.class) {
                if (!setupDone) {

                    if (!EnvironmentHelper.inArcadiaTest) {
                        setupMysql();
                    }

                    setupDone = true;
                } else {
                    log.info("Setup already had been performed earlier");
                }
            }
        } else {
            log.info("Setup already had been performed earlier");
        }
    }

    private static void setupMysql() throws Exception {
        log.info("Setting up mysql");
        TransactionalMetrikaDataSource dataSource = new DataSourceFactory().getDataSource();
        dataSource.setHost(EnvironmentHelper.mysqlHost);
        dataSource.setPort(EnvironmentHelper.mysqlPort);
        dataSource.setUser(EnvironmentHelper.mysqlUser);
        dataSource.setDb(EnvironmentHelper.mysqlDatabase);
        dataSource.setPassword(EnvironmentHelper.mysqlPassword);

        dataSource.afterPropertiesSet();

        var databases = new MySqlJdbcTemplate(dataSource).query("SHOW DATABASES", RowMappers.STRING);

        if (databases.contains("conv_main") && databases.contains("rbac") && databases.contains("dicts") && EnvironmentHelper.allowMysqlPopulationSkip) {
            log.info("Databases already exists. Skipping DB population");
            return;
        }

        TestSetupHelper.populateDB(
                dataSource,
                ResourceHelper.mysqlResources("00_mysql_schema_conv_main.sql", "00_mysql_schema_dicts.sql", "00_mysql_schema_rbac.sql", "10_mysql_data_conv_main.sql", "10_mysql_data_rbac.sql")
        );
    }
}
