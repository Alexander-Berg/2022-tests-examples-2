package ru.yandex.metrika.dbclients.clickhouse;

import java.util.stream.StreamSupport;

import org.apache.commons.lang3.mutable.MutableLong;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

@Ignore
public class HttpTemplateImplTest {
    /**
     * ssh -L 8123:localhost:8123 mtlog01-01-1
     */
    private HttpTemplateImpl target;

    @Before
    public void setUp() throws Exception {
        target = new HttpTemplateImpl();
        ClickHouseSource db = new ClickHouseSource("localhost", 8123);
        target.setDb(db);
        target.afterPropertiesSet();

    }

   /* @Test
    public void test1() throws Exception {
        MutableLong sum = new MutableLong();
        for (int i =0 ; i < 10000; i++) {
            Iterable<Long> longs = target.queryStreaming("select CounterID,ClientHitID,UniqID,EventTime,Part,URL,EventData,Type,ClientEventTime, Encoding, WatchID,HitStartTime,VisitID,VisitStartTime from visor_events_2014071410450210021400 where  (1=1)  FORMAT TabSeparatedWithNamesAndTypes",
                    (rs, n) -> rs.getLong(1));
            longs.forEach(sum::add);
        }
        System.out.println(sum.longValue());
    }*/

    @Test
    public void testQueryStreaming() throws Exception {
        for (int i =0 ; i < 2; i++) {
            final MutableLong sum = new MutableLong();
            Iterable<Integer> iterable = target.queryStreaming("select * from system.numbers limit 10", (rs, rowNum) -> {
                return rs.getInt(1);
            });

            assertEquals(45,StreamSupport.stream(iterable.spliterator(), false).mapToInt(x -> x).sum());
        }
    }

    @Test
    public void testQueryStreaming2() throws Exception {
        for (int i =0 ; i < 10000; i++) {
            final MutableLong sum = new MutableLong();
            target.queryStreaming("select VisitID from visits_layer limit 10000", rs
                    -> sum.add(rs.getLong(1)));
            System.out.println("sum = " + sum);
        }

    }
}
