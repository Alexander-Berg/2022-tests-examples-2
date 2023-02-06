package ru.yandex.taxi.dmp.flink;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;

import lombok.experimental.UtilityClass;
import org.apache.flink.api.common.ExecutionConfig;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.PojoTypeInfo;
import org.apache.flink.api.java.typeutils.TypeExtractor;
import org.apache.flink.api.java.typeutils.runtime.PojoSerializer;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

@UtilityClass
public class SerializationTestUtils {
    public static <T> void assertPojoSerialization(Class<T> pojoClass) {
        final TypeInformation<T> typeInfo = TypeExtractor.createTypeInfo(pojoClass);
        assertTrue(typeInfo instanceof PojoTypeInfo);

        final ExecutionConfig config = new ExecutionConfig();
        config.disableGenericTypes();
        final PojoSerializer<T> pojoSerializer =
                ((PojoTypeInfo<T>) typeInfo).createPojoSerializer(config);
        assertNotNull(pojoSerializer);
    }

    public static byte[] serialize(Object obj) throws Exception {
        try (ByteArrayOutputStream b = new ByteArrayOutputStream()) {
            try (ObjectOutputStream o = new ObjectOutputStream(b)) {
                o.writeObject(obj);
                return b.toByteArray();
            }
        }
    }

    public static Object deserialize(byte[] bytes) throws Exception {
        try (ByteArrayInputStream b = new ByteArrayInputStream(bytes)) {
            try (ObjectInputStream o = new ObjectInputStream(b)) {
                return o.readObject();
            }
        }
    }
}
