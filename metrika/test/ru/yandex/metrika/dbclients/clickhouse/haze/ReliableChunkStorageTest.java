package ru.yandex.metrika.dbclients.clickhouse.haze;

import java.util.List;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.stream.Collectors;

import com.codahale.metrics.MetricRegistry;
import com.google.common.collect.Lists;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.clickhouse.settings.ClickHouseProperties;
import ru.yandex.metrika.dbclients.clickhouse.ClickHouseMRConfig;
import ru.yandex.metrika.dbclients.clickhouse.ClickHouseSource;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateLoadBalancer;
import ru.yandex.metrika.dbclients.clickhouse.MetrikaClickHouseProperties;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.chunk.clickhouse.haze.ChunkContextMysql;
import ru.yandex.metrika.util.chunk.clickhouse.haze.DoubleWriteTemplatesProvider;
import ru.yandex.metrika.util.chunk.clickhouse.haze.ReliableChunkStorage;
import ru.yandex.metrika.util.chunk.clickhouse.haze.SampledChunkDatabaseHazeCHMysql;
import ru.yandex.metrika.util.chunk.clickhouse.haze.WriteTemplatesProvider;
import ru.yandex.metrika.util.concurrent.Pools;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

@Ignore
public class ReliableChunkStorageTest {
    ReliableChunkStorage<ChunkRowForChecking> storage;
    static ExecutorService tpe = Pools.newNamedFixedThreadPool(6, "safe-chunk-storage-test");
    public static final String TABLE_PREFIX = "test_";
    @Before
    public void setUp(){
        Log4jSetup.basicSetup();
        ChunkRowDescriptor chunkDescriptor = new ChunkRowDescriptor();
        storage = new ReliableChunkStorage<>();
        storage.setChunkCHDatabase(createChunkDatabase(chunkDescriptor));
        storage.setChunkDescriptor(chunkDescriptor);
        storage.afterPropertiesSet();
        storage.setGcDeletedTimeout(2000);
        storage.setGcPreparedTimeout(2000);
    }

    private SampledChunkDatabaseHazeCHMysql createChunkDatabase(ChunkRowDescriptor chunkDescriptor) {
        MySqlJdbcTemplate dictionaryTemplate = getDictionaryTemplate();
        HttpTemplateLoadBalancer balancer = getBalancer();
        WriteTemplatesProvider writeTemplatesProvider = getWriteTemplatesProvider();
        MetricRegistry metricRegistry = new MetricRegistry();
        SampledChunkDatabaseHazeCHMysql database = new SampledChunkDatabaseHazeCHMysql();
        database.setDictionaryTemplate(dictionaryTemplate);
        database.setWriteTemplatesProvider(writeTemplatesProvider);
        database.setBalancer(balancer);
        database.setDictionaryTableName("test_reliable_storage");
        database.setMetricRegistry(metricRegistry);
        database.setTablePrefix(chunkDescriptor.tableNamePrefix());
        database.setWriteEnabled(true);
        database.afterPropertiesSet();
        return database;
    }


    @Test
    public void test() throws Exception {
        List<String> chunkIds = Lists.newArrayList();
        for (int i = 0; i < 10; i++) {
            List<ChunkRowForChecking> rows = Lists.newArrayList();
            for (int j = 0; j < 20; j++) {
                rows.add(new ChunkRowForChecking(i*100 + j, 200*i + j, "hello"+i*100+j));
            }
            chunkIds.add(storage.createChunk(rows).getChunkId());
        }

        for (String chunkId : chunkIds) {
            assertEquals(20, storage.correctRows(chunkId).size());
        }
        Set<String> writtenChunkIds = storage.list().stream().map(ChunkContextMysql::getChunkId).collect(Collectors.toSet());
        for (String chunkId : chunkIds) {
            assertTrue(writtenChunkIds.contains(chunkId));
        }

        storage.dropChunks(chunkIds.subList(0, 5));

        System.out.println(storage.list());
        System.out.println(storage.rows(chunkIds.get(0)).size());
        Thread.sleep(3000);
        for (int i = 5; i < chunkIds.size(); i++) {
            storage.dropChunk(chunkIds.get(i));
        }
        storage.gc();
    }

    @Test
    public void testStream() throws Exception {
        List<ChunkRowForChecking> rows = Lists.newArrayList();
        for (int j = 0; j < 2000; j++) {
            rows.add(new ChunkRowForChecking(j, j, "hello"+j));
        }

        String chunkId = storage.createChunkStream(rows.iterator()).getChunkId();

        List<String> stringVals = Lists.newArrayList();
        storage.forItems(chunkId, ChunkRowForChecking.COLUMNS, rs -> stringVals.add(rs.getString(3)));
        assertEquals(2000, stringVals.size());
        storage.dropChunk(chunkId);
        storage.gc();
    }

    private static MySqlJdbcTemplate getDictionaryTemplate() {
        return AllDatabases.getTemplate("localhost", 3309, "metrika", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_old"), "conv_main");
    }

    private static HttpTemplateLoadBalancer getBalancer() {
        HttpTemplateLoadBalancer balancer = new HttpTemplateLoadBalancer();
        balancer.setProperties(new MetrikaClickHouseProperties());
        balancer.setStickyFunction(new HttpTemplateLoadBalancer.PathLocalStickyFunction());
        balancer.setStopOnClickhouseException(false);
        balancer.setBreakLoadBalanceOnSocketTimeout(false);
        return balancer;
    }

    private static WriteTemplatesProvider getWriteTemplatesProvider() {
        ClickHouseProperties properties = new MetrikaClickHouseProperties();
        ClickHouseMRConfig clickHouseMRConfig = new ClickHouseMRConfig("test_storage", "test_storage");
        clickHouseMRConfig.setMaster(new ClickHouseSource("localhost", 8124,"test_storage"));
        clickHouseMRConfig.setReplica(new ClickHouseSource("127.0.0.1", 8125,"test_storage"));
        return new DoubleWriteTemplatesProvider(clickHouseMRConfig, properties);
    }
}
