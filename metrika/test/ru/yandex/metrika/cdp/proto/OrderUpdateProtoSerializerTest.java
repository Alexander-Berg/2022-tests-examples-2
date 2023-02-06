package ru.yandex.metrika.cdp.proto;

import java.time.Instant;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import org.junit.Test;

import ru.yandex.metrika.cdp.dto.core.EntityStatus;
import ru.yandex.metrika.cdp.dto.core.Order;
import ru.yandex.metrika.cdp.dto.core.OrderUpdate;
import ru.yandex.metrika.cdp.dto.core.UpdateType;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.cdp.common.FieldNames.Order.COST;
import static ru.yandex.metrika.cdp.common.FieldNames.Order.PRODUCTS;
import static ru.yandex.metrika.cdp.common.FieldNames.Order.REVENUE;


public class OrderUpdateProtoSerializerTest {

    @Test
    public void testE2E() {

        var order = new Order(
                1,
                2,
                3L,
                "aa",
                Instant.now(),
                Instant.now(),
                Instant.now(),
                10L,
                5L,
                "status",
                Map.of("a", 1, "b", 2),
                Map.of("attr1", Set.of("q", "w")),
                EntityStatus.ACTIVE
        );
        var clientUpdate = new OrderUpdate(
                order, UpdateType.UPDATE, UUID.randomUUID(),
                Set.of(REVENUE, COST, PRODUCTS),
                32123);

        var serializer = new OrderUpdateProtoSerializer();

        assertEquals(clientUpdate, serializer.deserialize(serializer.serialize(clientUpdate)));
    }
}
