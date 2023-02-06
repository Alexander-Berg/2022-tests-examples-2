package ru.yandex.metrika.api.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.constructor.contr.FeatureService;
import ru.yandex.metrika.api.management.client.counter.CodeOptionsService;
import ru.yandex.metrika.api.management.client.counter.CounterFlagsService;
import ru.yandex.metrika.api.management.client.counter.CounterOptionsService;
import ru.yandex.metrika.api.management.client.counter.CountersDao;
import ru.yandex.metrika.rbac.metrika.CountersRbac;

@Configuration
@Import({CounterOptionsServiceConfig.class, CodeOptionsServiceConfig.class, CountersDaoConfig.class,
        CountersRbacConfig.class, FeatureServiceConfig.class})
public class CounterFlagsServiceConfig {

    @Bean
    public CounterFlagsService counterFlagsService(CounterOptionsService counterOptionsService,
                                                   CodeOptionsService codeOptionsService,
                                                   CountersDao countersDao,
                                                   CountersRbac countersRbac,
                                                   FeatureService featureService) {
        return new CounterFlagsService(counterOptionsService, codeOptionsService, countersDao, countersRbac, featureService);
    }
}
