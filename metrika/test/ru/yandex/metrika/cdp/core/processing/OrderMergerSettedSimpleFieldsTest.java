package ru.yandex.metrika.cdp.core.processing;

import java.time.Instant;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import javax.annotation.Nonnull;

import com.google.common.collect.Lists;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.cdp.core.merge.FieldInfo;
import ru.yandex.metrika.cdp.dto.core.Order;
import ru.yandex.metrika.cdp.dto.core.UpdateType;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static ru.yandex.metrika.cdp.core.processing.OrderMerger.FINISH_DATE_TIME_FIELD_INFO;

@RunWith(Parameterized.class)
public class OrderMergerSettedSimpleFieldsTest extends AbstractOrderMergerTest {

    @Parameterized.Parameter(0)
    public UpdateType updateType;

    @Parameterized.Parameter(1)
    public FieldInfo<Order, ?> fieldInfo;

    @Parameterized.Parameters(name = "{0}: {1}")
    public static Collection<Object[]> operatingSystems() {
        return Lists.cartesianProduct(
                Arrays.asList(UpdateType.values()),
                // для всех остальных полей мы выставляем дефолты в Merger-e так что они всегда не null
                List.of(FINISH_DATE_TIME_FIELD_INFO)
        ).stream().map(List::toArray).collect(Collectors.toList());
    }

    @Test
    public void testMerge() {
        var oldOrder = getOldOrder();
        assertNotNull(fieldInfo.getter.apply(oldOrder));

        var newOrder = getNewOrder();
        fieldInfo.setter.accept(newOrder, null);

        var mergeResult = orderMerger.merge(newOrder, oldOrder, updateType, Set.of(fieldInfo.fieldId), UPLOADING_ID_1);
        assertNull(fieldInfo.getter.apply(mergeResult.getEntity()));
    }

    @Nonnull
    protected static Order getNewOrder() {
        return getEmptyOrder();
    }

    @Nonnull
    protected static Order getOldOrder() {
        var oldOrder = getEmptyOrder();
        oldOrder.setFinishDateTime(Instant.now());
        oldOrder.setRevenue(10L);
        oldOrder.setCost(5L);
        return oldOrder;
    }

}
