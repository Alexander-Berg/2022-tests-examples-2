package ru.yandex.metrika.util.stat;

import java.util.Arrays;
import java.util.List;

import com.google.common.collect.Lists;
import org.joda.time.DateTime;
import org.joda.time.LocalDate;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.clickhouse.settings.ClickHouseProperties;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateImpl;
import ru.yandex.metrika.dbclients.clickhouse.MetrikaClickHouseProperties;
import ru.yandex.metrika.spring.profile.StatEntry;
import ru.yandex.metrika.spring.profile.StatGatherer;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.chunk.ch2.CHOrmRepository;
import ru.yandex.metrika.util.chunk.ch2.CHOrmUtils;

/**
 * @author lemmsh
 * @since 4/22/14
 */

public class StatTest {

    long time = System.currentTimeMillis();

    private HttpTemplate getHttpTemplate() {
        ClickHouseProperties properties = new MetrikaClickHouseProperties();
        properties.setCompress(true);
        properties.setConnectionTimeout(5000);
        properties.setMaxThreads(1);
        properties.setSocketTimeout(30000);
        properties.setDataTransferTimeout(30000);
        properties.setApacheBufferSize(65536*2);
        properties.setBufferSize(65536*2);
        HttpTemplateImpl chTemplate = AllDatabases.getCHTemplate("localhost", 8123, "test");
        chTemplate.setProperties(properties);
        return chTemplate;
    }

    @Test
    @Ignore
    public void testOutputCommand() throws Exception {
        //StringBuilder sb = new StringBuilder();
        StatEntry entry = getEntry(0);
        //CHOutput commandOutput = new CHOutput(CHOrmUtils.getColNum(StatEntry.class));
        String s = CHOrmUtils.asString(Arrays.asList(entry, entry, entry, entry, entry), StatEntry.class);
        /*CHOrmUtils.dumpFields(entry, commandOutput);
        CHOrmUtils.dumpFields(entry, commandOutput);
        CHOrmUtils.dumpFields(entry, commandOutput);
        CHOrmUtils.dumpFields(entry, commandOutput);
        CHOrmUtils.dumpFields(entry, commandOutput);*/
        //System.out.println(Joiner.on("\t").join(CHOrmUtils.getColumnNames(StatEntry.class)));
        System.out.println(s);

    }

    @Test
    @Ignore
    public void testORM() throws Exception {

        //System.out.println(CHOrmUtils.getCreateTable(StatEntry.class, "testlog", CHOrmUtils.getCHMergeTreeCreateTable(StatEntry.class), true));


        //int colNum = CHOrmUtils.getColNum(StatEntry.class);
        //CHOutputRow output = new CHOutputRow(colNum);
        String s = CHOrmUtils.asString(Arrays.asList(getEntry(0)), StatEntry.class);//dumpFields(getEntry(0), output);
        System.out.println("s = " + s);
        //System.out.println(CHOrmUtils.getColumns(StatEntry.class));
        //System.out.println(output.toString());

    }

    @Test
    @Ignore
    public void testORMInsertion() throws Exception {
        final HttpTemplate httpTemplate = getHttpTemplate();
        final String tableName = "merged_tree_table";

        CHOrmRepository<StatEntry> statEntryCHOrmRepository = new CHOrmRepository<>(
                httpTemplate, tableName, StatEntry.class, CHOrmUtils.getCHMergeTreeCreateTable(StatEntry.class));

        List<StatEntry> entryList = Lists.newArrayList();
        for (int i = 0; i < 100; i++) {
            entryList.add(getEntry(i));
        }

        statEntryCHOrmRepository.saveAll(entryList);

    }

    private StatEntry getEntry(int i) {
        StatEntry entry = StatGatherer.getEntry();
        entry.setAccuracy("medium");
        entry.setAuthType("uid");
        entry.setCounterIds("101024");
        entry.setEventDate(new LocalDate(time + i));
        entry.setEventDateTime(new DateTime(time + i));
        entry.setDimensions(null);
        entry.setFilters(null);
        entry.setHost("metrika-dev");
        entry.setIp("0:0:0:0:0:0:0:1");
        entry.setLinesReturned(1);
        entry.setMetrics("ym:s:under18AgePercentage");
        entry.setLimit(100);
        entry.setOffset(1);
        entry.setPreset(null);
        entry.setRows(28499);
        entry.setSampling(0.1);
        entry.setSourceType("interface");
        entry.setTiming(287);
        entry.setUid(41L);
        entry.setUrl("stat/v1/data");
        return entry;
    }

}
