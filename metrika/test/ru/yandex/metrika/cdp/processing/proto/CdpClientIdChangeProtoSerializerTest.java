package ru.yandex.metrika.cdp.processing.proto;

import org.junit.Test;

import ru.yandex.metrika.cdp.processing.dto.matching.CdpClientIdChange;

import static org.junit.Assert.assertEquals;

public class CdpClientIdChangeProtoSerializerTest {

    @Test
    public void testE2E() {
        var cdpClientIdChange = new CdpClientIdChange(
                1,
                2,
                3,
                CdpClientIdChange.ChangeType.ADD
        );

        var serializer = new CdpClientIdChangeProtoSerializer();

        assertEquals(cdpClientIdChange, serializer.deserialize(serializer.serialize(cdpClientIdChange)));
    }

}
