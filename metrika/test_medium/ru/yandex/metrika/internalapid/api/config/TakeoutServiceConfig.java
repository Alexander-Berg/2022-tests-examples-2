package ru.yandex.metrika.internalapid.api.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.metrika.api.management.client.counter.CounterOptionsDao;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.internalapid.common.IntapiCountersService;
import ru.yandex.metrika.internalapid.takeout.TakeoutService;

@Configuration
public class TakeoutServiceConfig {

    @Autowired
    @Qualifier("convMainTemplate")
    protected MySqlJdbcTemplate convMain;

    @Autowired
    @Qualifier("dictsTemplate")
    protected MySqlJdbcTemplate dicts;

    @Autowired
    @Qualifier("rbacTemplate")
    protected MySqlJdbcTemplate rbac;

    @Autowired
    protected CounterOptionsDao counterOptionsDao;

    @Autowired
    protected IntapiCountersService intapiCountersService;

    @Bean
    public TakeoutService takeoutService() {
        return new TakeoutService(convMain, rbac, counterOptionsDao, intapiCountersService);
    }

}
