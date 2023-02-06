package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.streaming.util.MockDeserializationSchema;

public class TypedMockDeserializationSchema<T> extends MockDeserializationSchema<T> {

    private final TypeInformation<T> typeInformation;

    public TypedMockDeserializationSchema(Class<T> tClass) {
        this.typeInformation = TypeInformation.of(tClass);
    }

    @Override
    public TypeInformation<T> getProducedType() {
        return typeInformation;
    }
}
