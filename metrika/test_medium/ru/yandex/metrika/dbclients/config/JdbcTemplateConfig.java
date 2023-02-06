package ru.yandex.metrika.dbclients.config;

import java.util.Properties;

import javax.sql.DataSource;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ImportResource;
import org.springframework.transaction.PlatformTransactionManager;

import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.dbclients.mysql.DataSourceFactory;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.mysql.TransactionUtil;
import ru.yandex.metrika.dbclients.mysql.TransactionalMetrikaDataSource;
import ru.yandex.metrika.util.app.Settings;

@Configuration
@ImportResource({
        "classpath:/ru/yandex/metrika/util/common-jdbc.xml",
        "classpath:/ru/yandex/metrika/util/common-tx.xml"
})
public class JdbcTemplateConfig {

    @Bean
    public DataSource convMainDataSource(
            @Qualifier("convDataSourceFactory") DataSourceFactory dataSourceFactory
    ) {
        TransactionalMetrikaDataSource dataSource = dataSourceFactory.getDataSource(10);

        dataSource.setHost(EnvironmentHelper.mysqlHost);
        dataSource.setPort(EnvironmentHelper.mysqlPort);
        dataSource.setUser(EnvironmentHelper.mysqlUser);
        dataSource.setPassword(EnvironmentHelper.mysqlPassword);
        dataSource.setDb("conv_main");

        Properties properties = new Properties();
        properties.setProperty("serverTimezone", "Europe/Moscow");
        properties.setProperty("characterEncoding", "utf-8");
        dataSource.setConnectionProperties(properties);

        return dataSource;
    }

    @Bean
    public MySqlJdbcTemplate convMainTemplate(DataSource convMainDataSource) throws Exception {
        MySqlTestSetup.globalSetup();
        return new MySqlJdbcTemplate(convMainDataSource);
    }

    @Bean
    public Settings settings() {
        return new Settings();
    }

    @Bean
    public TransactionUtil transactionUtil(PlatformTransactionManager atomikosTxManager) {
        return new TransactionUtil(atomikosTxManager);
    }

}
