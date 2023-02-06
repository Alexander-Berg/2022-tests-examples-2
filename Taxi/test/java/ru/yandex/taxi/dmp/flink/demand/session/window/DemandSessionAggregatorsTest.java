package ru.yandex.taxi.dmp.flink.demand.session.window;

import com.esotericsoftware.kryo.Kryo;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class DemandSessionAggregatorsTest {

    @Test
    public void testSerializationEmpty() throws Exception {
        final Kryo kryo = KryoTestUtils.prepareKryo();
        kryo.register(DemandSessionAggregators.class, new DemandSessionAggregators.KryoSerializer());
        var aggregators = new DemandSessionAggregators();

        var bytes = KryoTestUtils.serialize(kryo, aggregators);
        var newAggregators = KryoTestUtils.deserialize(kryo, bytes, DemandSessionAggregators.class);

        assertEquals(aggregators.getAggregators().size(), newAggregators.getAggregators().size());
        assertEquals(aggregators.get("pin_cnt", Long.class).getResult(),
                newAggregators.get("pin_cnt", Long.class).getResult());
    }

    @Test
    public void testSerialization() throws Exception {
        final Kryo kryo = KryoTestUtils.prepareKryo();
        kryo.register(DemandSessionAggregators.class, new DemandSessionAggregators.KryoSerializer());
        var aggregators = new DemandSessionAggregators();
        aggregators.add(DemandSessionTestUtils.DEFAULT_PIN);
        aggregators.add(DemandSessionTestUtils.DEFAULT_ORDER);
        aggregators.add(DemandSessionTestUtils.DEFAULT_OFFER);

        System.out.println(aggregators.get("multiorder_flg").getResult());

        var bytes = KryoTestUtils.serialize(kryo, aggregators);
        var newAggregators = KryoTestUtils.deserialize(kryo, bytes, DemandSessionAggregators.class);

        assertEquals(aggregators.getAggregators().size(), newAggregators.getAggregators().size());
        assertEquals(aggregators.get("pin_cnt", Long.class).getResult(),
                newAggregators.get("pin_cnt", Long.class).getResult());
    }
}
