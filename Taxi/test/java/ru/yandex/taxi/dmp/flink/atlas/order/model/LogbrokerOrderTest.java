package ru.yandex.taxi.dmp.flink.atlas.order.model;

import org.junit.jupiter.api.Test;

import ru.yandex.taxi.dmp.flink.SerializationTestUtils;
import ru.yandex.taxi.dmp.flink.atlas.order.model.logbroker.LogbrokerOrder;

class LogbrokerOrderTest {
    @Test
    void testPojoType() {
        SerializationTestUtils.assertPojoSerialization(LogbrokerOrder.class);
    }
}
