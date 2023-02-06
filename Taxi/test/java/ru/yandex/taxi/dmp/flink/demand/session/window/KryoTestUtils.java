package ru.yandex.taxi.dmp.flink.demand.session.window;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;

import com.esotericsoftware.kryo.Kryo;
import com.esotericsoftware.kryo.io.Input;
import com.esotericsoftware.kryo.io.Output;

public class KryoTestUtils {
    private KryoTestUtils() {
    }

    public static Kryo prepareKryo() {
        final Kryo kryo = new Kryo();
        kryo.setReferences(false);
        return kryo;
    }

    public static byte[] serialize(Kryo kryo, Object object) throws Exception {
        var os = new ByteArrayOutputStream();
        try {
            try (Output output = new Output(os)) {
                kryo.writeObject(output, object);
            }
        } finally {
            os.close();
        }
        return os.toByteArray();
    }

    public static <T> T deserialize(Kryo kryo, byte[] bytes, Class<T> tClass) throws Exception {
        try (InputStream is = new ByteArrayInputStream(bytes)) {
            try (Input input = new Input(is)) {
                return kryo.readObject(input, tClass);
            }
        }
    }
}
