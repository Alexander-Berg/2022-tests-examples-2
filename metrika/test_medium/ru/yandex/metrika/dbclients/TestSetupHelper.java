package ru.yandex.metrika.dbclients;

import javax.sql.DataSource;

import org.springframework.core.io.Resource;
import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;

public class TestSetupHelper {
    public static void populateDB(DataSource dataSource, Resource... resources) {
        var resourceDatabasePopulator = new ResourceDatabasePopulator(resources);
        resourceDatabasePopulator.setContinueOnError(true);
        resourceDatabasePopulator.execute(dataSource);
    }
}
