package ru.yandex.taxi.dmp.flink.connectors.logbroker.producer;

import org.junit.jupiter.api.Test;

import ru.yandex.kikimr.persqueue.auth.Credentials;
import ru.yandex.taxi.dmp.flink.SerializationTestUtils;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.common.SerializableSupplier;

import static org.junit.jupiter.api.Assertions.assertEquals;

class LogbrokerProducerConfigTest {
    public static final String TOPIC = "dummy";

    @Test
    public void testSerializable() throws Exception {
        final LogbrokerProducerConfig config = LogbrokerProducerConfig.builder(TOPIC).build();

        final byte[] bytes = SerializationTestUtils.serialize(config);
        final LogbrokerProducerConfig deserializeConfig =
                (LogbrokerProducerConfig) SerializationTestUtils.deserialize(bytes);
        assertEquals(TOPIC, deserializeConfig.getTopic());
    }

    @Test
    public void testSerializableWithAuth() throws Exception {
        final String token = "testToken";
        final LogbrokerProducerConfig config = LogbrokerProducerConfig
                .builder(TOPIC, Credentials.oauth(token))
                .build();

        final byte[] bytes = SerializationTestUtils.serialize(config);
        final LogbrokerProducerConfig deserializeConfig =
                (LogbrokerProducerConfig) SerializationTestUtils.deserialize(bytes);
        assertEquals(TOPIC, deserializeConfig.getTopic());
        assertEquals(Credentials.CredentialsType.OAUTH, deserializeConfig.getCredentials().getType());
        assertEquals(token, deserializeConfig.getCredentials().getValue());
    }

    @Test
    public void testSerializableWithSupplier() throws Exception {
        final String token = "testToken";
        final LogbrokerProducerConfig config = LogbrokerProducerConfig
                .builder(TOPIC, (SerializableSupplier<Credentials>) () -> Credentials.oauth(token))
                .build();

        final byte[] bytes = SerializationTestUtils.serialize(config);
        final LogbrokerProducerConfig deserializeConfig =
                (LogbrokerProducerConfig) SerializationTestUtils.deserialize(bytes);
        assertEquals(TOPIC, deserializeConfig.getTopic());
        assertEquals(Credentials.CredentialsType.OAUTH, deserializeConfig.getCredentials().getType());
        assertEquals(token, deserializeConfig.getCredentials().getValue());
    }
}
