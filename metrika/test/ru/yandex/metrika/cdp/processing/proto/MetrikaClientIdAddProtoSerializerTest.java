package ru.yandex.metrika.cdp.processing.proto;

import java.time.Instant;

import org.junit.Test;

import ru.yandex.metrika.cdp.processing.dto.matching.MetrikaClientIdAdd;

import static org.junit.Assert.assertEquals;

public class MetrikaClientIdAddProtoSerializerTest {

    @Test
    public void testE2E() {
        var metrikaClientIdChange = new MetrikaClientIdAdd(
                1,
                2,
                3,
                4,
                Instant.now()
        );

        var serializer = new MetrikaClientIdAddProtoSerializer();

        assertEquals(metrikaClientIdChange, serializer.deserialize(serializer.serialize(metrikaClientIdChange)));
    }

}
