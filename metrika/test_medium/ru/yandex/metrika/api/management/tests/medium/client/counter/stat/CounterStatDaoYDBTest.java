package ru.yandex.metrika.api.management.tests.medium.client.counter.stat;

import java.time.LocalDate;
import java.util.Collection;
import java.util.Comparator;
import java.util.List;
import java.util.Random;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import com.google.common.collect.Lists;
import org.hamcrest.MatcherAssert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.api.management.client.counter.stat.CounterActivityFull;
import ru.yandex.metrika.api.management.client.counter.stat.CounterActivityRaw;
import ru.yandex.metrika.api.management.client.counter.stat.CounterStatDaoYDB;
import ru.yandex.metrika.api.management.config.CounterStatDaoYDBConfig;
import ru.yandex.metrika.util.collections.F;

import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assert.assertEquals;

@RunWith(SpringRunner.class)
@ContextConfiguration(classes = CounterStatDaoYDBConfig.class)
public class CounterStatDaoYDBTest {

    @Autowired
    private CounterStatDaoYDB counterStatDaoYDB;

    @Test
    public void testCreateNewTable() {
        String table = counterStatDaoYDB.createNewTable();
        counterStatDaoYDB.updateCurrentTable(table);
        assertEquals(table, counterStatDaoYDB.getCurrentTable());
    }

    @Test
    public void testInsertAndGet() {
        String table = counterStatDaoYDB.createNewTable();
        counterStatDaoYDB.updateCurrentTable(table);
        Random r = new Random(0);
        var data = IntStream.range(1, 101).mapToObj(i -> genActivity(r, i)).collect(Collectors.toList());
        var counters = F.map(data, CounterActivityFull::getCounterId);

        counterStatDaoYDB.insert(data, table);
        var actualData = counterStatDaoYDB.getCountersActivity(counters, true);

        assertEquals(data.size(), actualData.size());
        actualData.sort(Comparator.comparingInt(CounterActivityRaw::getCounterId));

        projectionEqualsAssert(data, actualData, CounterActivityRaw::getLast2HoursVisits);
        projectionEqualsAssert(data, actualData, CounterActivityRaw::getTodayHits);
//        projectionEqualsAssert(data, actualData, CounterActivityRaw::getWeekHttpsVisits);

    }

    private <T> void projectionEqualsAssert(Collection<CounterActivityFull> expectedData, Collection<CounterActivityRaw> actualData, Function<CounterActivityRaw, T> projection) {
        MatcherAssert.assertThat(
                F.map(actualData, projection).toArray(),
                equalTo(F.map(expectedData, projection).toArray())
        );
    }

    @Test
    public void testInsertAndGetAllId() {
        String table = counterStatDaoYDB.createNewTable();
        counterStatDaoYDB.updateCurrentTable(table);
        Random r = new Random(0);
        var data = IntStream.range(1, 101).mapToObj(i -> genActivity(r, i)).collect(Collectors.toList());
        var counters = F.map(data, CounterActivityFull::getCounterId);

        counterStatDaoYDB.insert(data, table);

        var actualId = Lists.newArrayList(counterStatDaoYDB.getCounters("True"));
        actualId.sort(Comparator.naturalOrder());

        assertEquals(counters.size(), actualId.size());
        MatcherAssert.assertThat(
                counters.toArray(),
                equalTo(actualId.toArray())
        );
    }

    private CounterActivityFull genActivity(Random r, int id) {
        return new CounterActivityFull(id, LocalDate.now(),
                r.nextInt(100), r.nextInt(100), r.nextInt(100),
                genWeekList(r), genWeekList(r), genWeekList(r),
                r.nextInt(100),  r.nextInt(100),  r.nextInt(100),
                r.nextInt(100),  r.nextInt(100),  r.nextInt(100),
                r.nextInt(100),  r.nextInt(100),  r.nextInt(100),
                r.nextInt(100), r.nextInt(100), r.nextInt(100),
                genWeekList(r), genWeekList(r), genWeekList(r),
                r.nextInt(100),  r.nextInt(100),  r.nextInt(100),
                r.nextInt(100),  r.nextInt(100),  r.nextInt(100),
                r.nextInt(100),  r.nextInt(100),  r.nextInt(100));
    }

    private List<Integer> genWeekList(Random r) {
        return IntStream.range(0, 7).map(i -> r.nextInt()).boxed().collect(Collectors.toList());
    }

}
