package ru.yandex.metrika.segments.clickhouse.model;

import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ClickHouse;
import ru.yandex.metrika.segments.clickhouse.ast.SelectQuery;
import ru.yandex.metrika.segments.site.schema.MtLog;

/**
 * Created by orantius on 12/28/15.
 */
public class SelectQueryImplTest {
    @Test
    public void testSql() throws Exception {
        SelectQuery q = ClickHouse.select(MtLog.Visits.UserAgent).build();
        String s = q.asSql();
        System.out.println("s = " + s);

    }
}
