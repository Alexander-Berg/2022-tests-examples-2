package ru.yandex.metrika.restream.sharder.stat;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.function.Consumer;
import java.util.stream.LongStream;

import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import org.junit.Before;
import org.junit.Test;

import static java.util.Comparator.comparing;
import static org.junit.Assert.assertEquals;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.COUNTER_ID;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.COUNTER_ID_2;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.EMPTY_VISIT;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.EMPTY_VISIT_2;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.HOST_ID;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.HOST_ID_2;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.HOST_ID_3;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.slotIds;
import static ru.yandex.metrika.restream.sharder.stat.StatsTestsUtils.vs;

public class StatServiceTest {

    private StatService statService;
    private StatsStorageYdb mockStorage;
    private StatsCollector mockCollector;

    @Before
    public void setUp() {
        mockStorage = mock(StatsStorageYdb.class);
        mockCollector = mock(StatsCollector.class);
        statService =  new StatService(HOST_ID, mockCollector, mockStorage);
    }

    @Test
    public void updateStatsTest() {
        var rows = List.of(vs(EMPTY_VISIT), vs(EMPTY_VISIT_2));
        statService.updateStats(rows);

        verify(mockCollector, times(1)).updateStats(rows);
    }

    @Test
    public void flushStatsTest() {
        var mockResF = (CompletableFuture<Void>) mock(CompletableFuture.class);
        var slotIds = slotIds(1, 2, 3);
        var statRows = List.of(
                new StatRow(COUNTER_ID, HOST_ID, 1, 10, 1, slotIds),
                new StatRow(COUNTER_ID, HOST_ID, 1, 10, 1, slotIds)
        );
        doReturn(statRows).when(mockCollector).statRows(eq(HOST_ID));
        doReturn(mockResF).when(mockStorage).saveAsync(eq(statRows));
        doReturn(null).when(mockResF).join();

        statService.flushStats();

        verify(mockCollector, times(1)).statRows(HOST_ID);
        verify(mockStorage, times(1)).saveAsync(statRows);
        verify(mockResF, times(1)).join();
    }

    @Test
    public void getAllStatsAsyncTest() {
        var statRows = new ArrayList<>(List.of(
                // у первого счётчика слоты разных длин
                new StatRow(COUNTER_ID, HOST_ID, 1, 10, 12, slotIds(60, 72)),
                new StatRow(COUNTER_ID, HOST_ID_2, 3, 40, 15, slotIds(60, 75)),
                // у второго счётчика есть один устаревший слот (HOST_ID_3, slotId = 45)
                new StatRow(COUNTER_ID_2, HOST_ID, 5, 1000, 15, slotIds(60, 75, 90)),
                new StatRow(COUNTER_ID_2, HOST_ID_2, 40, 400, 15, slotIds(60, 75)),
                new StatRow(COUNTER_ID_2, HOST_ID_3, 20, 100, 15, slotIds(45, 60, 75))
        ));
        statRows.sort(comparing(StatRow::getCounterId).thenComparing(StatRow::getHostId));
        doReturn(60L).when(mockCollector).getDeadLineSlotId();
        doAnswer(invocation -> {
            statRows.forEach(invocation.getArgument(0, Consumer.class));
            return CompletableFuture.completedFuture(null);
        }).when(mockStorage).readAllOrderedStream(any(Consumer.class));

        var stats = statService.getAllStatsAsync().join();
        verify(mockStorage, times(1)).readAllOrderedStream(any(Consumer.class));

        var expected = new Int2ObjectOpenHashMap<StatRow>();
        expected.put(COUNTER_ID, new StatRow(COUNTER_ID, "", 4, 50, 3, slotIds(LongStream.iterate(60, l -> l <= 87, l -> l + 3).toArray())));
        expected.put(COUNTER_ID_2, new StatRow(COUNTER_ID_2, "", 58, 1466, 15, slotIds(60, 75, 90)));

        assertEquals(expected, stats);
    }
}
