package ru.yandex.metrika.lb.read.processing;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.CompletableFuture;
import java.util.stream.IntStream;
import java.util.stream.Stream;

import javax.annotation.Nonnull;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;

import ru.yandex.kikimr.persqueue.compression.CompressionCodec;
import ru.yandex.kikimr.persqueue.consumer.StreamListener;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerReadResponse;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageBatch;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageData;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageMeta;
import ru.yandex.metrika.lb.read.ReinitializingStreamConsumer;
import ru.yandex.metrika.lb.serialization.BatchSerializer;
import ru.yandex.metrika.lb.serialization.Serializer;

import static java.util.stream.Collectors.toList;

public class ProcessingStreamListenerTest {

    private final Random random = new Random();
    private Map<String, MessageData> messageMap;
    private int sourcesCnt;

    @Before
    public void setUp() throws Exception {
        messageMap = new HashMap<>();
    }

    @Test
    public void testOrderSimple() {
        var collectingProcessor = new CollectingProcessor();
        var listener = ProcessingStreamListener.withProcessor(collectingProcessor)
                .withConsumer(Mockito.mock(ReinitializingStreamConsumer.class))
                .withSerializer(new StringSerializer())
                .withSorting()
                .build();
        sourcesCnt = 2;
        var consumerReadResponse = ccr(
                batch(
                        "topic1", 0,
                        Stream.concat(
                                IntStream.range(0, 10).mapToObj(i -> message(0, i)),
                                IntStream.range(0, 10).mapToObj(i -> message(1, i))
                        ).toArray(MessageData[]::new)
                )
        );
        listener.onReadDelegate(consumerReadResponse, new DummyReadResponder());
        collectingProcessor.assertOrder();
    }

    @Test
    public void testOrderBatch() {
        var collectingProcessor = new CollectingProcessor();
        var listener = ProcessingStreamListener.withProcessor(collectingProcessor)
                .withConsumer(Mockito.mock(ReinitializingStreamConsumer.class))
                .withBatchSerializer(new SplittingBatchStringSerializer())
                .withSorting()
                .build();
        sourcesCnt = 2;
        var consumerReadResponse = ccr(
                batch(
                        "topic1", 0,
                        Stream.concat(
                                IntStream.range(0, 10).mapToObj(i -> batchMessage(0, i)),
                                IntStream.range(0, 10).mapToObj(i -> batchMessage(1, i))
                        ).toArray(MessageData[]::new)
                )
        );
        listener.onReadDelegate(consumerReadResponse, new DummyReadResponder());
        collectingProcessor.assertOrder();
    }

    private ConsumerReadResponse ccr(MessageBatch... batches) {
        return new ConsumerReadResponse(
                Arrays.asList(batches),
                0
        );
    }


    @SuppressWarnings("SameParameterValue")
    private MessageBatch batch(String topic, int partition, MessageData... messages) {
        return new MessageBatch(
                topic,
                partition,
                Arrays.asList(messages)
        );
    }

    private MessageData message(int sourceId, long seqNo) {
        var content = "message_from_source_" + sourceId + "_no_" + seqNo;
        var messageData = getMessageData(sourceId, seqNo, content);
        messageMap.put(content, messageData);
        return messageData;
    }

    private MessageData batchMessage(int sourceId, long seqNo) {
        var strings = IntStream.range(0, random.nextInt(10) + 1)
                .mapToObj(i -> "message_from_source_" + sourceId + "_no_" + seqNo + "_part_" + i)
                .collect(toList());
        var messageData = getMessageData(sourceId, seqNo, String.join(",", strings));
        strings.forEach(s -> messageMap.put(s, messageData));
        return messageData;
    }

    @Nonnull
    private MessageData getMessageData(int sourceId, long seqNo, String content) {
        assert sourceId <= sourcesCnt;
        return new MessageData(
                content.getBytes(),
                0,
                new MessageMeta(
                        ("source" + sourceId).getBytes(),
                        seqNo,
                        seqNo * 1000 + random.nextInt(sourcesCnt),
                        0,
                        "",
                        CompressionCodec.RAW,
                        Map.of()
                )
        );
    }


    private static class StringSerializer implements Serializer<String> {
        @Override
        public byte[] serialize(String s) {
            return s.getBytes();
        }

        @Override
        public String deserialize(byte[] bytes) {
            return new String(bytes);
        }
    }

    private static class SplittingBatchStringSerializer implements BatchSerializer<String> {
        @Override
        public byte[] serialize(Collection<String> strings) {
            return String.join(",", strings).getBytes();
        }

        @Override
        public Collection<String> deserialize(byte[] bytes) {
            return Arrays.asList(new String(bytes).split(","));
        }
    }

    private class CollectingProcessor implements LogbrokerSimpleProcessor<String> {

        private final List<List<String>> packs = new ArrayList<>();

        @Override
        public CompletableFuture<Void> process(List<String> messages) {
            packs.add(messages);
            return CompletableFuture.completedFuture(null);
        }

        /**
         * Идея проверки такая:
         * 1. Для каждого сообщения, все предыдущие с тем же sourceId должны иметь seqNo меньше текущего
         * 1. Для каждого сообщения, все предыдущие с тем другим sourceId должны иметь createTimeMs меньше текущего
         */
        public void assertOrder() {
            for (List<String> pack : packs) {
                var enrichedPack = pack.stream().map(messageMap::get).collect(toList());
                Map<String, Long> maxSeqNoForSource = new HashMap<>();
                Map<String, Long> maxCreateTimeMsForSource = new HashMap<>();
                for (MessageData messageData : enrichedPack) {
                    var sourceId = new String(messageData.getMessageMeta().getSourceId());
                    var seqNo = messageData.getMessageMeta().getSeqNo();
                    var createTimeMs = messageData.getMessageMeta().getCreateTimeMs();
                    var maxPrevSeqNo = maxSeqNoForSource.getOrDefault(sourceId, -1L);
                    if (seqNo < maxPrevSeqNo) {
                        Assert.fail("Meet seqNo " + seqNo + " after seqNo " + maxPrevSeqNo + " for source " + sourceId);
                    }
                    maxCreateTimeMsForSource.forEach((innerSourceId, prevMaxCreateTimeMs) -> {
                        if (!innerSourceId.equals(sourceId) && createTimeMs < prevMaxCreateTimeMs) {
                            Assert.fail("Meet createTimeMs " + createTimeMs + " in source " + sourceId +
                                    " after createTimeMs " + prevMaxCreateTimeMs + " in source " + innerSourceId);
                        }
                    });

                    maxSeqNoForSource.put(sourceId, seqNo);
                    maxCreateTimeMsForSource.compute(
                            sourceId,
                            (innerSourceId, prevMaxCreateTimeMs) ->
                                    prevMaxCreateTimeMs != null && prevMaxCreateTimeMs > createTimeMs ?
                                            prevMaxCreateTimeMs : createTimeMs
                    );
                }
            }
        }
    }

    private static class DummyReadResponder implements StreamListener.ReadResponder {

        @Override
        public void commit() {

        }
    }


}
