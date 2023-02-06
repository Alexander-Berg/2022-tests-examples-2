package ru.yandex.metrika.restream.sharder.stat;

import java.time.Duration;
import java.util.List;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.test.ManualClock;

import static java.util.Comparator.comparing;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.BIG_VISIT;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.BIG_VISIT_2;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.COUNTER_ID;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.COUNTER_ID_2;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.EMPTY_VISIT;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.EMPTY_VISIT_2;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.HOST_ID;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.slotIds;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.vs;

public class StatsCollectorTest {

    private static final Duration ONE_MINUTE = Duration.ofMinutes(1);
    private static final int SLOTS_COUNT = 5;

    private ManualClock manualClock;
    private StatsCollector statsCollector;

    @Before
    public void setUp() {
        manualClock = new ManualClock();
        statsCollector = new StatsCollector(SLOTS_COUNT, (int) ONE_MINUTE.getSeconds(), manualClock);
    }

    @Test
    public void basicTest() {
        statsCollector.updateStats(List.of(vs(EMPTY_VISIT)));
        var statRows = statsCollector.statRows(HOST_ID);
        Assert.assertEquals(1, statRows.size());
        Assert.assertEquals(
                new StatRow(COUNTER_ID, HOST_ID, 1, EMPTY_VISIT.getSerializedSize(), (int) ONE_MINUTE.getSeconds(), slotIds(0)),
                statRows.get(0)
        );
    }

    @Test
    public void multipleSlotsTest() {
        statsCollector.updateStats(List.of(vs(EMPTY_VISIT)));
        manualClock.offset(ONE_MINUTE);
        statsCollector.updateStats(List.of(vs(EMPTY_VISIT)));
        var statRows = statsCollector.statRows(HOST_ID);
        Assert.assertEquals(1, statRows.size());
        Assert.assertEquals(
                new StatRow(COUNTER_ID, HOST_ID, 2, EMPTY_VISIT.getSerializedSize() * 2L, (int) ONE_MINUTE.getSeconds(), slotIds(0, ONE_MINUTE.getSeconds())),
                statRows.get(0)
        );
    }

    @Test
    public void multipleSlotsAndDifferentVisitsTest() {
        statsCollector.updateStats(List.of(vs(EMPTY_VISIT)));
        manualClock.offset(ONE_MINUTE);
        statsCollector.updateStats(List.of(vs(BIG_VISIT)));
        var statRows = statsCollector.statRows(HOST_ID);
        Assert.assertEquals(1, statRows.size());
        Assert.assertEquals(
                new StatRow(COUNTER_ID, HOST_ID, 2, EMPTY_VISIT.getSerializedSize() + BIG_VISIT.getSerializedSize(), (int) ONE_MINUTE.getSeconds(), slotIds(0, ONE_MINUTE.getSeconds())),
                statRows.get(0)
        );
    }

    @Test
    public void multipleSlotsAndDifferentVisitsFromDifferentCountersTest() {
        statsCollector.updateStats(List.of(vs(EMPTY_VISIT)));
        manualClock.offset(ONE_MINUTE);
        statsCollector.updateStats(List.of(vs(BIG_VISIT), vs(EMPTY_VISIT_2)));
        manualClock.offset(ONE_MINUTE.multipliedBy(2));
        statsCollector.updateStats(List.of(vs(BIG_VISIT_2)));
        var statRows = statsCollector.statRows(HOST_ID);
        statRows.sort(comparing(StatRow::getCounterId));
        var slotIds = slotIds(0, ONE_MINUTE.getSeconds(), ONE_MINUTE.getSeconds() * 2, ONE_MINUTE.getSeconds() * 3);
        Assert.assertEquals(2, statRows.size());
        Assert.assertEquals(
                new StatRow(COUNTER_ID, HOST_ID, 2, EMPTY_VISIT.getSerializedSize() + BIG_VISIT.getSerializedSize(), (int) ONE_MINUTE.getSeconds(), slotIds),
                statRows.get(0)
        );
        Assert.assertEquals(
                new StatRow(COUNTER_ID_2, HOST_ID, 2, EMPTY_VISIT_2.getSerializedSize() + BIG_VISIT_2.getSerializedSize(), (int) ONE_MINUTE.getSeconds(), slotIds),
                statRows.get(1)
        );
    }

    @Test
    public void cleanUpTest() {
        statsCollector.updateStats(List.of(vs(EMPTY_VISIT)));
        var statRows = statsCollector.statRows(HOST_ID);
        Assert.assertEquals(1, statRows.size());
        Assert.assertEquals(
                new StatRow(COUNTER_ID, HOST_ID, 1, EMPTY_VISIT.getSerializedSize(), (int) ONE_MINUTE.getSeconds(), slotIds(0)),
                statRows.get(0)
        );

        manualClock.offset(ONE_MINUTE.multipliedBy(SLOTS_COUNT));

        statsCollector.updateStats(List.of(vs(EMPTY_VISIT)));
        statRows = statsCollector.statRows(HOST_ID);
        Assert.assertEquals(1, statRows.size());
        Assert.assertEquals(
                new StatRow(COUNTER_ID, HOST_ID, 1, EMPTY_VISIT.getSerializedSize(), (int) ONE_MINUTE.getSeconds(), slotIds(ONE_MINUTE.getSeconds() * 5)),
                statRows.get(0)
        );
    }
}
