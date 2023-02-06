package ru.yandex.metrika.remarketingd.export.lb;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Random;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.type.TypeReference;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.lb.serialization.json.JsonDtoSerializer;
import ru.yandex.metrika.retargeting.CollectorSegmentData;
import ru.yandex.metrika.retargeting.export.BsBatchSerializer;

import static java.util.Arrays.asList;
import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
public class BsBatchSerializerTest {
    public static class CollectorSegmentDataDeserializable extends CollectorSegmentData {
        @JsonCreator
        public CollectorSegmentDataDeserializable(
                @JsonProperty("timestamp") int timestamp,
                @JsonProperty("segmentId") int segmentId,
                @JsonProperty("uid") long uid,
                @JsonProperty("version") long version,
                @JsonProperty("delete") boolean delete
        ) {
            super(timestamp, segmentId, uid, version, delete, 0, 0);
        }
    }

    private JsonDtoSerializer<CollectorSegmentDataDeserializable> internalSerializer = new JsonDtoSerializer<>(new TypeReference<CollectorSegmentDataDeserializable>() {});
    private BsBatchSerializer<CollectorSegmentDataDeserializable> serializer = new BsBatchSerializer<> ();

    @Parameterized.Parameter
    public int batchSize;

    @Parameterized.Parameters(name = "batchSize = {0}")
    public static Collection<Object[]> parameters() {
        return asList(
                new Object[]{0},
                new Object[]{1},
                new Object[]{10},
                new Object[]{100},
                new Object[]{500}
        );
    }

    @Before
    public void setUp() throws Exception {
        serializer.setSerializer(internalSerializer);
        serializer.setMaxBatchSize(100);
    }

    @Test
    public void checkSerializeRevertible() {
        ArrayList<CollectorSegmentDataDeserializable> items = new ArrayList<>();
        Random rnd = new Random();
        for (int i = 0; i < batchSize; i++){
           items.add(
                   new CollectorSegmentDataDeserializable(
                       rnd.nextInt(1000000000),
                       rnd.nextInt(1000000000),
                       rnd.nextInt(1000000000),
                       rnd.nextInt(1000000000),
                       rnd.nextBoolean()
                   )
           );
        }
        assertEquals(items, serializer.deserialize(serializer.serialize(items)));
    }
}
