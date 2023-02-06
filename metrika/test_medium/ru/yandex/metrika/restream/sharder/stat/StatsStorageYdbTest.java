package ru.yandex.metrika.restream.sharder.stat;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.dbclients.config.YdbConfig;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;

import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.COUNTER_ID;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.HOST_ID;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.slotIds;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class StatsStorageYdbTest {

    @Autowired
    public StatsStorageYdb statsStorageYdb;

    @BeforeClass
    public static void beforeClass() {
        YdbSetupUtil.setupYdbFolders("");
    }

    @Before
    public void setUp() {
        YdbSetupUtil.truncateTablesIfExists(EnvironmentHelper.ydbDatabase + "/" + StatsStorageYdb.TABLE_NAME);
    }

    @Test
    public void simpleSaveAndRead() {
        var statRow = new StatRow(COUNTER_ID, HOST_ID, 1, 1, 1, slotIds(0));
        statsStorageYdb.saveAsync(List.of(statRow)).join();

        Assert.assertEquals(List.of(statRow), getAllRowsOrdered());
    }

    @Test
    public void saveALotOfRows() {
        var statRows = IntStream.range(0, 100_000)
                .mapToObj(i -> new StatRow(COUNTER_ID + i, HOST_ID, 1, 1, 1, slotIds(0)))
                .collect(Collectors.toList());

        Collections.shuffle(statRows);
        statsStorageYdb.saveAsync(statRows).join();

        statRows.sort(Comparator.comparing(StatRow::getCounterId).thenComparing(StatRow::getHostId));

        Assert.assertEquals(statRows, getAllRowsOrdered());
    }

    private List<StatRow> getAllRowsOrdered() {
        var statRows = new ArrayList<StatRow>();
        statsStorageYdb.readAllOrderedStream(statRows::add).join();
        return statRows;
    }

    @Configuration
    @Import(YdbConfig.class)
    public static class Config {
        @Bean
        public StatsStorageYdb statsStorageYdb(YdbTemplate template) {
            return new StatsStorageYdb(template);
        }
    }

}
