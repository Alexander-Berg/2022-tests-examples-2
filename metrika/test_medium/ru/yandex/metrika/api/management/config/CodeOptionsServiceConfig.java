package ru.yandex.metrika.api.management.config;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.management.client.counter.CodeOptionsDao;
import ru.yandex.metrika.api.management.client.counter.CodeOptionsService;
import ru.yandex.metrika.api.management.client.counter.InformerDao;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;

@Configuration
@Import({JdbcTemplateConfig.class})
public class CodeOptionsServiceConfig {

    @Bean
    CodeOptionsDao codeOptionsDao(@Qualifier("convMainTemplate") MySqlJdbcTemplate convMain) {
        return new CodeOptionsDao(convMain);
    }

    @Bean
    InformerDao informerDao(@Qualifier("convMainTemplate") MySqlJdbcTemplate convMain) {
        var result = new InformerDao();
        result.setJdbcTemplate(convMain);
        return result;
    }

    @Bean
    public CodeOptionsService codeOptionsService(CodeOptionsDao codeOptionsDao,
                                                 InformerDao informerDao) {
        return new CodeOptionsService(codeOptionsDao, informerDao);
    }
}
