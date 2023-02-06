package ru.yandex.metrika.api.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.management.client.counter.stat.CounterStatDaoYDB;
import ru.yandex.metrika.dbclients.config.YdbConfig;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.YdbSchemeManager;
import ru.yandex.metrika.util.PropertyUtils;
import ru.yandex.metrika.util.PropertyUtilsYdb;

import static org.mockito.Mockito.mock;

@Configuration
@Import({YdbConfig.class})
public class CounterStatDaoYDBConfig {

    @Bean
    public PropertyUtilsYdb propertyUtilsYdb(YdbTemplate ydbTemplate) {
        PropertyUtilsYdb ydbPropUtils = new PropertyUtilsYdb();
        ydbPropUtils.setYdbTemplate(ydbTemplate);
        return ydbPropUtils;
    }

    @Bean
    public CounterStatDaoYDB counterStatDaoYDB(YdbTemplate ydb,
                                               PropertyUtilsYdb propertyUtilsYdb,
                                               YdbSchemeManager ydbSchemeManager) {
        var counterStatDaoYDB = new CounterStatDaoYDB(ydb, mock(PropertyUtils.class), propertyUtilsYdb, ydbSchemeManager);
        counterStatDaoYDB.setTableNamePrefix("test_counter_stat_");
        return counterStatDaoYDB;
    }

}
