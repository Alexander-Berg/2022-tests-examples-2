package ru.yandex.metrika.cloud.formatter.common.util;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

import ru.yandex.kikimr.persqueue.producer.AsyncProducer;
import ru.yandex.kikimr.persqueue.producer.transport.message.inbound.ProducerInitResponse;
import ru.yandex.kikimr.persqueue.producer.transport.message.inbound.ProducerWriteResponse;

class FakeLbProducer implements AsyncProducer {
    List<Message> messages = new ArrayList<>();
    long maxSeqNo = -1;

    @Override
    public CompletableFuture<ProducerInitResponse> init() {
        return null;
    }

    @Override
    public CompletableFuture<ProducerWriteResponse> write(byte[] data, long seqNo, long timestamp) {
        if (seqNo > maxSeqNo) {
            maxSeqNo = seqNo;
            messages.add(new Message(data, seqNo, timestamp));
            return CompletableFuture.completedFuture(new ProducerWriteResponse(seqNo, seqNo, true));
        }
        return CompletableFuture.completedFuture(new ProducerWriteResponse(seqNo, seqNo, false));
    }

    @Override
    public CompletableFuture<Void> closeFuture() {
        return null;
    }

    @Override
    public void close() {

    }

    record Message(byte[] data, long seqNo, long timestamp) {
    }
}
