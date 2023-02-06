package ru.yandex.taxi.conversation.util;

import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

import ru.yandex.kikimr.persqueue.compression.CompressionCodec;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageData;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageMeta;
import ru.yandex.taxi.conversation.logbroker.read.ConsumerId;
import ru.yandex.taxi.conversation.logbroker.read.Message;
import ru.yandex.taxi.conversation.logbroker.read.Partition;

public class LogbrokerMessageHelper {

    private static final String DEFAULT_PARTITION;
    private static final String DEFAULT_CONSUMER;

    static {
        DEFAULT_PARTITION = "rt3.kafka-bs--conversation@development--conversation-in-messages";
        DEFAULT_CONSUMER  = "/support_platform_conversation/functional_test/conversation-in-messages-consumer";
    }

    public static Message createMessage(byte[] data) {
        return createMessage(data, DEFAULT_CONSUMER);
    }

    public static Message createMessage(byte[] data, String consumerId) {
        return createMessage(data, consumerId, DEFAULT_PARTITION);
    }

    public static Message createMessage(byte[] data, String consumerId, String partition) {
        return new Message(
                Partition.create(partition, 1),
                List.of(new MessageData(
                        data,
                        0,
                        new MessageMeta(
                                new byte[0],
                                1,
                                0,
                                0,
                                null,
                                CompressionCodec.RAW,
                                Map.of()
                        )
                )),
                new CompletableFuture<>(),
                new ConsumerId(consumerId)
        );
    }
}
