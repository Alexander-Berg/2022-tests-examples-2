package ru.yandex.metrika.direct.config;

import javax.sql.DataSource;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ImportResource;

import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.dbclients.mysql.DataSourceFactory;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.direct.dict.smart.order.target.phrases.MySqlPerformanceFilterDao;
import ru.yandex.metrika.direct.dict.target.phrases.MySqlDynamicConditionsDao;
import ru.yandex.metrika.util.concurrent.Pools;

@ImportResource("/ru/yandex/metrika/util/common-jdbc.xml")
@Configuration
public class DirectDictJdbcTestConfig {

    @Bean(name = {"mysql_misc"})
    public DataSource mysqlMisc(DataSourceFactory convDataSourceFactory) {
        var dataSource = convDataSourceFactory.getDataSource(5);
        dataSource.setHost(EnvironmentHelper.mysqlHost);
        dataSource.setPort(EnvironmentHelper.mysqlPort);
        dataSource.setUser(EnvironmentHelper.mysqlUser);
        dataSource.setPassword(EnvironmentHelper.mysqlPassword);
        dataSource.setDb("dicts");
        return dataSource;
    }

    @Bean
    public MySqlJdbcTemplate miscTemplate(
            DataSourceFactory convDataSourceFactory,
            @Qualifier("mysql_misc") DataSource mysqlMisc
    ) throws Exception {
        MySqlTestSetup.globalSetup();
        return convDataSourceFactory.getTemplate(mysqlMisc);
    }

    @Bean
    public MySqlDynamicConditionsDao mySqlDynamicConditionsDao(MySqlJdbcTemplate miscTemplate) {
        return new MySqlDynamicConditionsDao(
                miscTemplate,
                Pools.newNamedFixedThreadPool(2, "mysql-dynamic-conditions-dao-pool")
        );
    }

    @Bean
    public MySqlPerformanceFilterDao mySqlPerformanceFilterDao(MySqlJdbcTemplate miscTemplate) {
        return new MySqlPerformanceFilterDao(
                miscTemplate,
                Pools.newNamedFixedThreadPool(2, "mysql-performance-filter-dao-pool")
        );
    }
}
