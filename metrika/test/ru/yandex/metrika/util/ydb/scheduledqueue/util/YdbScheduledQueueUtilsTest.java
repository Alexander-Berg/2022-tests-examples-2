package ru.yandex.metrika.util.ydb.scheduledqueue.util;

import java.util.List;

import org.junit.Test;

import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.ydb.scheduledqueue.model.YdbScheduledRequest;
import ru.yandex.metrika.util.ydb.scheduledqueue.util.YdbScheduledQueueUtils.ShardRoutedBatch;

import static org.junit.Assert.assertEquals;

public class YdbScheduledQueueUtilsTest {

    @Test
    public void checkSplitInTransactionsKeepsOrder() {
        // Проверяем, что после разделения порядок элементов в ответе сохраняется.
        // Это нужно для коррекности работы push-dispatcher
        List<Integer> source = List.of(1, 2, 3, 4, 5, 6);
        List<List<YdbScheduledRequest<Integer>>> splitResult = YdbScheduledQueueUtils.splitInTransactions(
                F.map(source, i -> new YdbScheduledRequest<>(0, null, null, null, i, null)),
                x -> 1,
                2);
        List<List<Integer>> target = F.map(splitResult, batch -> F.map(batch, YdbScheduledRequest::getPayload));
        List<List<Integer>> expected = List.of(List.of(1, 2), List.of(3, 4), List.of(5, 6));
        assertEquals(expected, target);
    }

    @Test
    public void checkRouteToShardsKeepsOrder() {
        // Проверяем, что после распределения по шардам порядок элементов в ответе сохраняется.
        // Это нужно для коррекности работы push-dispatcher
        List<List<Integer>> source = List.of(List.of(1, 2), List.of(3, 4), List.of(5, 6));
        List<ShardRoutedBatch<Integer>> routed = YdbScheduledQueueUtils.routeToShards(
                F.map(source, batch -> F.map(batch, i -> new YdbScheduledRequest<>(0, null, null, null, i, null))),
                List.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10));
        List<List<Integer>> target = F.map(routed, batch -> F.map(batch.requests(), YdbScheduledRequest::getPayload));
        assertEquals(source, target);
    }
}
