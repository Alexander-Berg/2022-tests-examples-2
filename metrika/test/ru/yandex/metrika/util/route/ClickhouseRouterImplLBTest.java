package ru.yandex.metrika.util.route;

import com.google.common.collect.Lists;
import org.apache.logging.log4j.Level;
import org.junit.Ignore;
import org.junit.Test;
import org.mockito.Mockito;

import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.util.log.Log4jSetup;
import ru.yandex.metrika.util.route.layers.LayerInfoProvider;

/**
 * @author jkee
 */

@Ignore
public class ClickhouseRouterImplLBTest {
    @Test
    public void testName() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        RouteConfigSimple s1 = new RouteConfigSimple();
        s1.setHost("localhost");
        s1.setPort(11221);

        RouteConfigSimple s2= new RouteConfigSimple();
        s2.setHost("localhost");
        s2.setPort(11222);

        RouteConfigSimple s3 = new RouteConfigSimple();
        s3.setHost("localhost");
        s3.setPort(11223);

        RouteConfigLoadBalance routeConfigLoadBalance = new RouteConfigLoadBalance();
        routeConfigLoadBalance.setNodes(Lists.newArrayList(s1, s2, s3));

        ClickhouseRouterImplLB router = new ClickhouseRouterImplLB();
        LayerInfoProvider dao = Mockito.mock(LayerInfoProvider.class);
        Mockito.when(dao.getLayer(Mockito.anyInt())).thenReturn(1);
        router.setCounterDao(dao);

        router.createRouteAndPut(1, routeConfigLoadBalance);

        for (int i = 0; i < 10000; i++) {
            HttpTemplate routeForLayer = router.getRouteForLayer(1);
            routeForLayer.ping();
            Thread.sleep(500);
        }



    }
}
