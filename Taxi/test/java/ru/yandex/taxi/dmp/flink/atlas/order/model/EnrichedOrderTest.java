package ru.yandex.taxi.dmp.flink.atlas.order.model;

import org.junit.jupiter.api.Test;

import ru.yandex.taxi.dmp.flink.SerializationTestUtils;

class EnrichedOrderTest {
    @Test
    void testPojoType() {
        SerializationTestUtils.assertPojoSerialization(EnrichedOrder.class);
    }
}
