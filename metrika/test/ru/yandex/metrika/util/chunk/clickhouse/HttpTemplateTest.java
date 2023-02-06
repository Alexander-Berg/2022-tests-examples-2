package ru.yandex.metrika.util.chunk.clickhouse;

import java.util.List;

import com.google.common.collect.Lists;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.clickhouse.response.ClickHouseResponse;
import ru.yandex.metrika.chunks.visitlog.VisitLog;
import ru.yandex.metrika.dbclients.clickhouse.ClickHouseSource;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateImpl;
import ru.yandex.metrika.util.log.Log4jSetup;


/**
 * @author jkee
 */

public class HttpTemplateTest {
    @Test
    @Ignore
    public void testName() throws Exception {
        Log4jSetup.basicSetup();
        ClickHouseSource db = new ClickHouseSource("localhost", 38123);
        db.setDb("visit_log");
        HttpTemplateImpl old = new HttpTemplateImpl();
        old.setDb(db);
        old.afterPropertiesSet();
        HttpTemplateImpl compressed = new HttpTemplateImpl();
        compressed.setDb(db);
        compressed.afterPropertiesSet();

        String chunk = "VisitCache_Chunk_201307312049021502010";

        List<Long> results = getLongs(compressed, chunk);
        List<Long> resultsOld = getLongs(old, chunk);
        System.out.println(resultsOld.size());
        System.out.println(results.size());
        System.out.println(resultsOld.equals(results));

    }

    @Test
    @Ignore
    public void testJson() throws Exception {

        String sql = "Select VisitID, avg(UserID), avg(Duration), any(StartURL), 0/0 " +
                "from merge.visits where StartDate = toDate('2013-08-30')" +
                "and CounterID = 101024 group by VisitID limit 10 " +
                "FORMAT JSONCompact";
        ClickHouseSource db = new ClickHouseSource("localhost", 38123);
        HttpTemplateImpl template = new HttpTemplateImpl();
        template.setDb(db);
        template.afterPropertiesSet();
        ClickHouseResponse clickhouseResponse = template.queryJson(sql);
        System.out.println(clickhouseResponse);

    }

    private List<Long> getLongs(HttpTemplate compressed, String chunk) {
        long t = System.currentTimeMillis();
        List<Long> results = Lists.newArrayList();
        Iterable<VisitLog> visitLogs = compressed.query(getSql(chunk), VisitLog.newRowMapper());
        /*for (VisitLog visitLog : visitLogs) { METR-10088
            results.add(visitLog.getIp());
        } */
        System.out.println(System.currentTimeMillis() - t);
        return results;
    }

    private String getSql(String chunk) {
        return "select " +
                    VisitLog.COLUMNS_CH + " from " + chunk + " limit 100000";
    }
}
