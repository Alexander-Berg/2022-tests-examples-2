package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer;

import org.junit.jupiter.api.Test;

import ru.yandex.kikimr.persqueue.auth.Credentials;
import ru.yandex.taxi.dmp.flink.SerializationTestUtils;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.common.SerializableSupplier;

import static org.junit.jupiter.api.Assertions.assertEquals;

class LogbrokerConsumerConfigTest {
    public static final String TOPIC = "dummyTopic";
    public static final String CONSUMER = "dummyConsumer";

    @Test
    public void testSerializable() throws Exception {
        final LogbrokerConsumerConfig config = LogbrokerConsumerConfig.builder(TOPIC, CONSUMER).build();

        final byte[] bytes = SerializationTestUtils.serialize(config);
        final LogbrokerConsumerConfig deserializeConfig =
                (LogbrokerConsumerConfig) SerializationTestUtils.deserialize(bytes);
        assertEquals(TOPIC, deserializeConfig.getTopicPath());
        assertEquals(CONSUMER, deserializeConfig.getConsumerPath());
    }

    @Test
    public void testSerializableWithAuth() throws Exception {
        final String token = "testToken";
        final LogbrokerConsumerConfig config = LogbrokerConsumerConfig
                .builder(TOPIC, CONSUMER, Credentials.oauth(token))
                .build();

        final byte[] bytes = SerializationTestUtils.serialize(config);
        final LogbrokerConsumerConfig deserializeConfig =
                (LogbrokerConsumerConfig) SerializationTestUtils.deserialize(bytes);
        assertEquals(TOPIC, deserializeConfig.getTopicPath());
        assertEquals(CONSUMER, deserializeConfig.getConsumerPath());
        assertEquals(Credentials.CredentialsType.OAUTH, deserializeConfig.getCredentials().getType());
        assertEquals(token, deserializeConfig.getCredentials().getValue());
    }

    @Test
    public void testSerializableWithSupplier() throws Exception {
        final String token = "testToken";
        final LogbrokerConsumerConfig config = LogbrokerConsumerConfig
                .builder(TOPIC, CONSUMER, (SerializableSupplier<Credentials>) () -> Credentials.oauth(token))
                .build();

        final byte[] bytes = SerializationTestUtils.serialize(config);
        final LogbrokerConsumerConfig deserializeConfig =
                (LogbrokerConsumerConfig) SerializationTestUtils.deserialize(bytes);
        assertEquals(TOPIC, deserializeConfig.getTopicPath());
        assertEquals(CONSUMER, deserializeConfig.getConsumerPath());
        assertEquals(Credentials.CredentialsType.OAUTH, deserializeConfig.getCredentials().getType());
        assertEquals(token, deserializeConfig.getCredentials().getValue());
    }
}
