package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils;

import java.io.IOException;

import com.google.common.primitives.Longs;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;

public class LongDeserializationSchema implements DeserializationSchema<Long> {

    @Override
    public Long deserialize(byte[] message) throws IOException {
        return Longs.fromByteArray(message);
    }

    @Override
    public boolean isEndOfStream(Long nextElement) {
        return false;
    }

    @Override
    public TypeInformation<Long> getProducedType() {
        return TypeInformation.of(Long.class);
    }
}
