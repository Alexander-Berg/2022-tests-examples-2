package ru.yandex.metrika.util.chunk.clickhouse;

import java.util.Collections;
import java.util.List;

import com.google.common.collect.Lists;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.dbclients.clickhouse.ClickHouseSource;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateLoadBalancer;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

/**
 * @author lopashev
 * @since 09.09.14
 */
@Ignore("METRIQA-936")
public class HttpTemplateLoadBalancerTest {
    @Test
    public void testSimple() throws Exception {
        HttpTemplateLoadBalancer balancer = HttpTemplateLoadBalancer.prepare();
        ClickHouseSource source = new ClickHouseSource("", 0);
        List<ClickHouseSource> list = Collections.singletonList(source);
        assertNotNull(balancer.getTemplate(list));
        assertEquals(source, balancer.getTemplate(list).getDb());
    }

    @Test
    public void testBalance() throws Exception {
        HttpTemplateLoadBalancer balancer = HttpTemplateLoadBalancer.prepare();
        ClickHouseSource source1 = new ClickHouseSource("", 0);
        ClickHouseSource source2 = new ClickHouseSource("", 1);
        List<ClickHouseSource> list = Lists.newArrayList(source1, source2);
        ClickHouseSource expected = balancer.getTemplate(list).getDb();
        int count = 0;
        for (int i = 0; i < 100; i++) {
            ClickHouseSource rotated = balancer.getTemplate(list).getDb();
            if (expected == rotated) count++;
        }
        assertEquals(100, count);
    }
}
