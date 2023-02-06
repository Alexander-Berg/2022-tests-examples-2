package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils;

import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import ru.yandex.kikimr.persqueue.compression.CompressionCodec;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageBatch;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageData;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageMeta;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.message.UnpackedMessageBatch;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.message.UnpackedMessageData;

public class MessageFactory {
    private MessageFactory() {
    }

    public static MessageBatch createMessageBatch(String topic, int size) {
        return createMessageBatch(topic, size, 0, 100);
    }

    public static MessageBatch createMessageBatch(String topic, int size, long offset, long ts) {
        return new MessageBatch(
                topic,
                0,
                IntStream.range(0, size)
                        .mapToObj(i -> new MessageData(
                                Integer.toString(i).getBytes(StandardCharsets.UTF_8),
                                offset + i,
                                createTestMessageMeta(ts + i)
                        ))
                        .collect(Collectors.toList())
        );
    }

    public static UnpackedMessageBatch<String> createUnpackedBatch(String topic, int size) {
        return createUnpackedBatch(topic, 0, size, 0, 100);
    }

    public static UnpackedMessageBatch<String> createUnpackedBatch(String topic,
                                                                   int partition,
                                                                   int size,
                                                                   long offset,
                                                                   long ts) {
        return new UnpackedMessageBatch<>(
                topic,
                partition,
                IntStream.range(0, size)
                        .mapToObj(i -> new UnpackedMessageData<>(
                                "test_" + i,
                                offset + i,
                                ts + i
                        ))
                        .collect(Collectors.toList())
        );
    }

    public static MessageMeta createTestMessageMeta(long createTimeMs) {
        return new MessageMeta(
                new byte[]{}, 0, createTimeMs, 0, "", CompressionCodec.RAW, Collections.emptyMap()
        );
    }
}
