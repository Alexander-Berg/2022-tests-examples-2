package ru.yandex.metrika.schedulerd.config;

import java.util.List;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ImportResource;

import ru.yandex.metrika.clusters.clickhouse.MtAggr;
import ru.yandex.metrika.clusters.clickhouse.MtAggrCluster;
import ru.yandex.metrika.clusters.clickhouse.factories.GeneralCHClusterFactory;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateFactory;
import ru.yandex.metrika.dbclients.clickhouse.MetrikaClickHouseProperties;
import ru.yandex.metrika.util.route.BalancedRoute;
import ru.yandex.metrika.util.route.RouteConfigSimple;
import ru.yandex.metrika.util.route.RouterLBConfig;
import ru.yandex.metrika.util.route.RouterLBFactoryParams;
import ru.yandex.metrika.util.route.layers.ConstantLayerProvider;
import ru.yandex.metrika.util.route.layers.LayerInfoProvider;

@Configuration
@ComponentScan({"ru.yandex.metrika.clusters.clickhouse.factories"})
@ImportResource({
        "classpath:ru/yandex/metrika/ch-router-factory.xml",
        "classpath:ru/yandex/metrika/mtaggr-router-config.xml",
})
public class MtAggrConfig {

    String host = EnvironmentHelper.clickhouseHost;
    int port = EnvironmentHelper.clickhousePort;
    String user = EnvironmentHelper.clickhouseUser;
    String password = EnvironmentHelper.clickhousePassword;

    @Bean
    MetrikaClickHouseProperties testMtAggrConnectionProperties() {
        MetrikaClickHouseProperties props = new MetrikaClickHouseProperties();
        props.setUser(user);
        props.setPassword(password);
        return props;
    }

    @Bean
    RouterLBConfig testRouterConfig() {
        var config = new RouterLBConfig();
        var route = new BalancedRoute();
        route.setLayer(1);
        route.setReplica(new RouteConfigSimple(host, port));
        config.setElements(List.of(route));
        return config;
    }

    @Bean
    LayerInfoProvider constantLayerProvider() {
        return new ConstantLayerProvider(0);
    }

    @Bean
    RouterLBFactoryParams testMtAggrParams(
            HttpTemplateFactory httpTemplateFactory,
            MetrikaClickHouseProperties testMtAggrConnectionProperties,
            RouterLBConfig testRouterConfig,
            LayerInfoProvider constantLayerProvider) {
        return new RouterLBFactoryParams(httpTemplateFactory, testMtAggrConnectionProperties, testRouterConfig, constantLayerProvider);
    }

    @Bean
    MtAggr testMtAggr(GeneralCHClusterFactory defaultGeneralCHClusterFactory, RouterLBFactoryParams testMtAggrParams) {
        return defaultGeneralCHClusterFactory.makeCluster(MtAggrCluster.class, testMtAggrParams);
    }
}
