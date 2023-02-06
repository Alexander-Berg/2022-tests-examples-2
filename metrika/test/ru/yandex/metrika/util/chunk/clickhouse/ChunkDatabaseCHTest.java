package ru.yandex.metrika.util.chunk.clickhouse;

import java.util.ArrayDeque;
import java.util.List;

import org.apache.logging.log4j.Level;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.chunks.visitlog.VisitLog;
import ru.yandex.metrika.dbclients.AbstractResultSet;
import ru.yandex.metrika.dbclients.clickhouse.ClickHouseSource;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateImpl;
import ru.yandex.metrika.util.log.Log4jSetup;

/**
 * @author orantius
 * @version $Id$
 * @since 7/16/12
 */
@Ignore("METRIQA-936")
public class ChunkDatabaseCHTest {
    HttpTemplateImpl template;
    ChunkDatabaseCH chunkDatabaseCH;
    @Test
    public void list() throws Exception {
        String sql = "select  "+VisitLog.COLUMNS_CH+" from VisitCache_Chunk_2012072214420404220 where CounterID=1022911 FORMAT TabSeparatedWithNamesAndTypes";
        List<VisitLog> query = template.query(sql,
                (rs, rowNum) -> {
                    System.out.println("rs = " + rowNum);
                    return new VisitLog((AbstractResultSet)rs);
                });
        for (VisitLog visitLog : query) {
            System.out.println("visitLog = " + visitLog);
        }
    }

    @Test
    public void streaming() throws Exception {
        String sql = "select  "+VisitLog.COLUMNS_CH+" from VisitCache_Chunk_2012072214420404220 where  CounterID=1022911 FORMAT TabSeparatedWithNamesAndTypes";
        template.queryStreaming(sql, rs -> {
            //VisitLog visitLog  = new VisitLog(rs);
            //System.out.println("visitLog = " + visitLog);
        });
    }

    //@Test
    public void testPerformance() throws Exception {
        Iterable<String> tableNames = template.query("SHOW TABLES",
                (rs, rowNum) -> rs.getString(1));
        ArrayDeque<Long> timeDeque = new ArrayDeque<>();
        for (String tableName: tableNames) {
            if (!tableName.contains("VisitCache_Chunk")) continue;
            template.queryStreaming("select  "+VisitLog.COLUMNS_CH+" from " + tableName + " FORMAT TabSeparatedWithNamesAndTypes",rs -> {
                //VisitLog visitLog = new VisitLog(rs);
                timeDeque.addLast(System.currentTimeMillis());
                if (timeDeque.size() > 1000000) {
                    System.out.println("rps: " + 1000*((double)timeDeque.size()/(System.currentTimeMillis() - timeDeque.getFirst())));
                    for(int i = 0; i < 100000; i++) {
                        timeDeque.removeFirst();
                    }
                }
            });
        }
    }

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.WARN);
        template = new HttpTemplateImpl();
        ClickHouseSource db = new ClickHouseSource("metricadb02c", 8123, "visit_log");
        template.setDb(db);
        template.afterPropertiesSet();
        chunkDatabaseCH = new ChunkDatabaseCH();
        chunkDatabaseCH.setHttpTemplate(template);
        chunkDatabaseCH.setTablePrefix("VisitCache_Chunk_");
    }

    public static void main(String[] args) {
        ChunkDatabaseCHTest chunkDatabaseCHTest = new ChunkDatabaseCHTest();
        try {
            chunkDatabaseCHTest.setUp();
            chunkDatabaseCHTest.testPerformance();
        } catch (Exception e) {
            e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
        }
    }

}
