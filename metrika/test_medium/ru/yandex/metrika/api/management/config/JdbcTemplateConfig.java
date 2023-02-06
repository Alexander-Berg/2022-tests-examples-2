package ru.yandex.metrika.api.management.config;

import java.util.List;
import java.util.Properties;

import javax.sql.DataSource;

import com.atomikos.jdbc.nonxa.AtomikosNonXADataSourceBean;
import org.postgresql.ds.PGPoolingDataSource;
import org.postgresql.ds.common.BaseDataSource;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ImportResource;
import org.springframework.jdbc.core.JdbcTemplate;

import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.mysql.DataSourceFactory;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.mysql.TransactionalMetrikaDataSource;
import ru.yandex.metrika.dbclients.postgres.PgDataSourceFactory;
import ru.yandex.metrika.dbclients.postgres.PgDataSourceProperties;

import static ru.yandex.metrika.config.EnvironmentHelper.postgresDatabase;
import static ru.yandex.metrika.config.EnvironmentHelper.postgresHost;
import static ru.yandex.metrika.config.EnvironmentHelper.postgresPassword;
import static ru.yandex.metrika.config.EnvironmentHelper.postgresPort;
import static ru.yandex.metrika.config.EnvironmentHelper.postgresUser;

@Configuration
@ImportResource({"classpath:/ru/yandex/metrika/util/common-jdbc.xml"})
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

    //one bean to bring them all, and in the darkness bind them
    @Bean(name = { "convMainTemplate", "countersTemplate", "mainTemplate" })
    public MySqlJdbcTemplate convMainTemplate(@Qualifier("convMainDataSource") DataSource convMainDataSource) {
        return new MySqlJdbcTemplate(convMainDataSource);
    }

    @Bean
    public DataSource rbacDataSource(
            @Qualifier("convDataSourceFactory") DataSourceFactory dataSourceFactory
    ) {
        TransactionalMetrikaDataSource dataSource = dataSourceFactory.getDataSource(10);

        dataSource.setHost(EnvironmentHelper.mysqlHost);
        dataSource.setPort(EnvironmentHelper.mysqlPort);
        dataSource.setUser(EnvironmentHelper.mysqlUser);
        dataSource.setPassword(EnvironmentHelper.mysqlPassword);
        dataSource.setDb("rbac");

        return dataSource;
    }

    @Bean
    public MySqlJdbcTemplate rbacTemplate(@Qualifier("rbacDataSource") DataSource rbacDataSource) {
        return new MySqlJdbcTemplate(rbacDataSource);
    }

    @Bean
    public JdbcTemplate pgSubscriptionsTemplate() {
        PgDataSourceProperties properties = new PgDataSourceProperties();
        properties.setHost(List.of(postgresHost));
        properties.setPort(postgresPort);
        properties.setUser(postgresUser);
        properties.setPool(true);
        properties.setDb(postgresDatabase);
        properties.setPassword(postgresPassword);

        BaseDataSource dataSourceProps = new PGPoolingDataSource();
        dataSourceProps.setLoadBalanceHosts(true);
        dataSourceProps.setConnectTimeout(30);
        dataSourceProps.setSocketTimeout(30);
        dataSourceProps.setTargetServerType("master");
        dataSourceProps.setPrepareThreshold(0);

        PgDataSourceFactory factory = new PgDataSourceFactory();
        factory.setProps(dataSourceProps);
        System.setProperty("ru.yandex.metrika.daemon.name", "management-common-ut");
        AtomikosNonXADataSourceBean dataSource = factory.getDataSource(properties);
        dataSource.setMaxPoolSize(5);

        return new JdbcTemplate(dataSource);
    }
}
