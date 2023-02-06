package ru.yandex.taxi.dmp.flink.atlas.order.model.multioffer;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import ru.yandex.taxi.dmp.flink.SerializationTestUtils;
import ru.yandex.taxi.dmp.flink.serialization.JsonMappingSchema;

import static org.junit.jupiter.api.Assertions.assertEquals;


class MultiOfferTest {

    private static JsonMappingSchema<MultiOffer> jsonMapping;

    @BeforeAll
    static void init() throws Exception {
        jsonMapping = new JsonMappingSchema<>(MultiOffer.class);
        jsonMapping.open((DeserializationSchema.InitializationContext) null);
    }

    @Test
    void parseMultiOffer() throws IOException {
        final MultiOffer multiOffer = jsonMapping.deserialize(Files.readAllBytes(Paths.get(
                "src/test/resources/multioffer/candidates.json"
        )));
        assertEquals("0434c720832626e81234ae9d8389fff", multiOffer.getOrderId());
        assertEquals(1611389034625L, multiOffer.getEventTimestamp());
        assertEquals(
                "72d17a92e23e475894f9ecf40e05cf51",
                multiOffer.getCandidates()[0].getCandidate().getDbid());
        assertEquals(
                "9a154e9581d24a05b372114be1a7ee63",
                multiOffer.getCandidates()[0].getCandidate().getUuid());
        assertEquals(
                "bf2gab443b844b798ed172dd530fe108",
                multiOffer.getCandidates()[2].getCandidate().getDbid());
        assertEquals(
                "3b7783fc5eb64f059cc99a44f6940630",
                multiOffer.getCandidates()[2].getCandidate().getUuid());
    }

    @Test
    void testPojoType() {
        SerializationTestUtils.assertPojoSerialization(MultiOffer.class);
    }
}
