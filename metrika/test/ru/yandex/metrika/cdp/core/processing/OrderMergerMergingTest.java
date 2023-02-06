package ru.yandex.metrika.cdp.core.processing;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import org.junit.Test;

import ru.yandex.metrika.cdp.dto.core.UpdateType;
import ru.yandex.metrika.util.collections.MapBuilder;

import static org.junit.Assert.assertEquals;

public class OrderMergerMergingTest extends AbstractOrderMergerTest {

    @Test
    public void updateMergeTest() {
        var oldOrder = getEmptyOrder();
        oldOrder.setCost(10L);
        oldOrder.setProducts(Map.of("a", 1, "b", 2));

        var newOrder = getEmptyOrder();
        newOrder.setRevenue(20L);
        newOrder.setProducts(Map.of("c", 3));

        var mergeResult = orderMerger.merge(newOrder, oldOrder, UpdateType.UPDATE, Set.of(), UPLOADING_ID_1);
        var entity = mergeResult.getEntity();


        assertEquals(newOrder.getRevenue(), entity.getRevenue());
        assertEquals(oldOrder.getCost(), entity.getCost());
        assertEquals(newOrder.getProducts(), entity.getProducts());
    }

    @Test
    public void appendMergeTest() {
        var oldProducts = new HashMap<>(Map.of("a", 1, "b", 2));
        var oldOrder = getEmptyOrder();
        oldOrder.setCost(10L);
        oldOrder.setProducts(oldProducts);

        var newProducts = new HashMap<>(Map.of("c", 3));
        var newOrder = getEmptyOrder();
        newOrder.setRevenue(20L);
        newOrder.setProducts(newProducts);

        var mergeResult = orderMerger.merge(newOrder, oldOrder, UpdateType.APPEND, Set.of(), UPLOADING_ID_1);
        var entity = mergeResult.getEntity();


        assertEquals(newOrder.getRevenue(), entity.getRevenue());
        assertEquals(oldOrder.getCost(), entity.getCost());
        assertEquals(
                MapBuilder.<String, Integer>builder()
                        .putAll(oldProducts)
                        .putAll(newProducts)
                        .build(),
                entity.getProducts()
        );
    }

}
