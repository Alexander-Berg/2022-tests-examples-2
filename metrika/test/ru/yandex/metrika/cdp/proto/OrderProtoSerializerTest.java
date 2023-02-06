package ru.yandex.metrika.cdp.proto;

import java.time.Instant;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.TimeUnit;

import org.junit.Test;

import ru.yandex.metrika.cdp.dto.core.EntityStatus;
import ru.yandex.metrika.cdp.dto.core.Order;

import static org.junit.Assert.assertEquals;

public class OrderProtoSerializerTest {

    @Test
    public void testE2E() {
        var order = new Order(
                1,
                2,
                3L,
                "3",
                Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)),
                Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)),
                Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)),
                100L,
                10L,
                "done",
                Map.of("iphone", 10, "ipad", 20),
                Map.of("test", Set.of("val1", "val2")),
                EntityStatus.ACTIVE
        );

        var serializer = new OrderProtoSerializer();

        assertEquals(order, serializer.deserialize(serializer.serialize(order)));
    }

}
