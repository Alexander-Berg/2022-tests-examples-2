package ru.yandex.metrika.schedulerd.cron.task;

import java.util.List;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableList;
import org.joda.time.DateTimeZone;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.commune.bazinga.impl.storage.BazingaStorage;
import ru.yandex.commune.zk2.ZkPath;
import ru.yandex.commune.zk2.primitives.observer.ZkPathObserver;
import ru.yandex.metrika.api.management.client.counter.stat.CounterActivityRaw;
import ru.yandex.metrika.api.management.client.counter.stat.CounterStatDaoYDB;
import ru.yandex.metrika.api.management.config.CounterStatDaoYDBConfig;
import ru.yandex.metrika.clusters.clickhouse.MtAggr;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.schedulerd.config.MtAggrConfig;
import ru.yandex.metrika.schedulerd.util.MtAggrCountersProcessor;
import ru.yandex.metrika.util.StringUtil;
import ru.yandex.metrika.util.io.IOUtils;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasProperty;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.in;
import static org.hamcrest.core.Is.is;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class CounterStatTaskTest {

    @Autowired
    CounterStatTask task;

    @Autowired
    CounterStatDaoYDB counterStatDaoYDB;

    @Test
    public void testTask() throws Exception {
        task.execute();

        var counters = ImmutableList.copyOf(counterStatDaoYDB.getCounters("True"));
        assertThat(counters, hasSize(100));

        var withRobots = counterStatDaoYDB.getCountersActivity(counters, true);
        var withoutRobots = counterStatDaoYDB.getCountersActivity(counters, false);

        var mapWithRobots = withRobots.stream().collect(Collectors.toMap(CounterActivityRaw::getCounterId, i -> i));
        var mapWithoutRobots = withoutRobots.stream().collect(Collectors.toMap(CounterActivityRaw::getCounterId, i -> i));

        assertThat(
                mapWithRobots.keySet(),
                both(everyItem(is(in(mapWithoutRobots.keySet().toArray()))))
                        .and(containsInAnyOrder(mapWithoutRobots.keySet().toArray()))
        );

        assertThat(
                mapWithRobots.values(),
                everyItem(hasProperty("weekVisits",
                        is(List.of(0, 0, 0, 0, 0, 0, 0, 42))))
        );

        assertThat(
                mapWithoutRobots.values(),
                everyItem(hasProperty("weekVisits",
                        is(List.of(0, 0, 0, 0, 0, 0, 0, 111))))
        );
    }

    @Configuration
    @Import({CounterStatDaoYDBConfig.class, MtAggrConfig.class})
    public static class TaskConfiguration {

        @Bean
        public MtAggrCountersProcessor mockedMtAggrCountersProcessor() {
            var mockedProcessor = mock(MtAggrCountersProcessor.class);
            when(mockedProcessor.getTimeZoneSafe(anyInt())).thenReturn(DateTimeZone.UTC);
            return mockedProcessor;
        }

        @Bean
        public BazingaStorage mockedBazinga() {
            return mock(BazingaStorage.class);
        }

        @Bean
        public ZkPathObserver mockedZkPathObserver() {
            return mock(ZkPathObserver.class);
        }

        @Bean
        public ZkPath zkPath() {
            return new ZkPath("/test");
        }

        @Bean
        public MySqlJdbcTemplate mockedConvMain() {
            return mock(MySqlJdbcTemplate.class);
        }

        private void initMtAggr(MtAggr testMtAggr) {
            String createCounterStatTableSql = IOUtils.resourceAsString(getClass(), "../../sql/create_basic_counter_stat_table.sql");
            String genDataSqlTemplate = IOUtils.resourceAsString(getClass(), "../../sql/gen_mtaggr_data.sql");
            String createHourTableSql = IOUtils.resourceAsString(getClass(), "../../sql/create_hour_table.sql");
            String genDataSql = StringUtil.substitute3(genDataSqlTemplate, "numberOfRows", 100);

            testMtAggr.mtaggr().getAllRoutes()
                    .forEach(r -> {
                        r.update(createCounterStatTableSql);
                        r.update(genDataSql);
                        r.update(createHourTableSql);
                    });
        }

        private void initYDB(CounterStatDaoYDB counterStatDaoYDB) {
            String name = counterStatDaoYDB.createNewTable();
            counterStatDaoYDB.updateCurrentTable(name);
        }

        @Bean
        public CounterStatTask counterStatTask(MtAggr testMtAggr,
                                               MtAggrCountersProcessor mockedMtAggrCountersProcessor,
                                               CounterStatDaoYDB counterStatDaoYDB) {
            initMtAggr(testMtAggr);
            initYDB(counterStatDaoYDB);
            return new CounterStatTask(testMtAggr, mockedMtAggrCountersProcessor, counterStatDaoYDB);
        }
    }
}
