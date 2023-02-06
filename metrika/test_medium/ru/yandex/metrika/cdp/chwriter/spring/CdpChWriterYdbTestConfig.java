package ru.yandex.metrika.cdp.chwriter.spring;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.metrika.cdp.dao.SchemaDao;
import ru.yandex.metrika.cdp.ydb.SchemaDaoYdb;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;

@Configuration
public class CdpChWriterYdbTestConfig {


    @Bean
    public SchemaDao schemaDao(YdbTemplate ydbTemplate) {
        return new SchemaDaoYdb(ydbTemplate, ydbTemplate.getDatabase() + "/schema");
    }

}
