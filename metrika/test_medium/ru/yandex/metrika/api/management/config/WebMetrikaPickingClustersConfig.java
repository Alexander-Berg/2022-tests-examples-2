package ru.yandex.metrika.api.management.config;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;

import ru.yandex.metrika.api.constructor.contr.CounterBignessService;
import ru.yandex.metrika.api.constructor.contr.CounterBignessServiceImpl;
import ru.yandex.metrika.api.constructor.contr.clusters.WebMetrikaPickingClusters;
import ru.yandex.metrika.clusters.clickhouse.MtGigaCluster;
import ru.yandex.metrika.clusters.clickhouse.MtNanoCluster;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.segments.core.dao.PickingClusters;

public class WebMetrikaPickingClustersConfig {

    @Bean
    CounterBignessService counterBignessService(@Qualifier("convMainTemplate") MySqlJdbcTemplate convMain) {
        return new CounterBignessServiceImpl(convMain);
    }

    @Bean
    PickingClusters webMetrikaClusters(MtGigaCluster mtGiga, MtNanoCluster mtNano, CounterBignessService counterBignessService) {
        return new WebMetrikaPickingClusters(counterBignessService, mtGiga, mtNano);
    }
}
