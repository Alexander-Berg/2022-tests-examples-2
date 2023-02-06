package ru.yandex.metrika.cdp.core.processing;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Set;

import org.junit.Test;

import ru.yandex.metrika.cdp.dto.core.UpdateType;

import static org.junit.Assert.assertEquals;

public class OrderMergerDefaultsTest extends AbstractOrderMergerTest {


    @Test
    public void setDefaultCostTest() {
        var newOrder = getEmptyOrder();

        var mergeResult = orderMerger.merge(newOrder, null, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        var entity = mergeResult.getEntity();

        assertEquals((Long) 0L, entity.getCost());
    }

    @Test
    public void setDefaultRevenueTest() {
        var newOrder = getEmptyOrder();

        var mergeResult = orderMerger.merge(newOrder, null, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        var entity = mergeResult.getEntity();

        assertEquals((Long) 0L, entity.getRevenue());
    }


    @Test
    public void forbidCreateDateTimeUpdateTest() {
        var oldOrder = getEmptyOrder();
        oldOrder.setCreateDateTime(Instant.now().minus(2, ChronoUnit.DAYS));

        var newOrder = getEmptyOrder();
        newOrder.setCreateDateTime(Instant.now().minus(1, ChronoUnit.DAYS));

        var mergeResult = orderMerger.merge(newOrder, oldOrder, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        var entity = mergeResult.getEntity();

        assertEquals(oldOrder.getCreateDateTime(), entity.getCreateDateTime());
    }

}
