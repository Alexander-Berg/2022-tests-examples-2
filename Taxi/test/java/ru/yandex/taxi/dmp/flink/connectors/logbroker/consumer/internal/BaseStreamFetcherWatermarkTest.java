package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal;

import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import javax.annotation.Nullable;

import org.apache.flink.api.common.eventtime.WatermarkGenerator;
import org.apache.flink.api.common.eventtime.WatermarkOutput;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.streaming.api.functions.AssignerWithPeriodicWatermarks;
import org.apache.flink.streaming.api.functions.AssignerWithPunctuatedWatermarks;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.runtime.operators.util.AssignerWithPeriodicWatermarksAdapter;
import org.apache.flink.streaming.runtime.operators.util.AssignerWithPunctuatedWatermarksAdapter;
import org.apache.flink.streaming.runtime.tasks.TestProcessingTimeService;
import org.apache.flink.util.SerializedValue;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;

import ru.yandex.kikimr.persqueue.consumer.BatchingStreamListener;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.message.UnpackedMessageBatch;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.message.UnpackedMessageData;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.message.UnpackedReadResponse;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.DummyStreamFetcher;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.TestSourceContext;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;

/**
 * копи паст тестов из org.apache.flink.streaming.connectors.kafka.internals.AbstractFetcherWatermarksTest
 */
public class BaseStreamFetcherWatermarkTest {
    public static final String TOPIC = "dummy";

    /**
     * Tests with watermark generators that have a periodic nature.
     */
    public static class PeriodicWatermarksSuite {

        public static Collection<WatermarkStrategy<Long>> getWatermarkStrategy() {
            return List.of(
                    new AssignerWithPeriodicWatermarksAdapter.Strategy<>(new PeriodicTestExtractor()),
                    WatermarkStrategy
                            .forGenerator((ctx) -> new PeriodicTestWatermarkGenerator())
                            .withTimestampAssigner((event, previousTimestamp) -> event)
            );
        }

        @ParameterizedTest
        @Timeout(5)
        @MethodSource("getWatermarkStrategy")
        public void testPeriodicWatermarks(WatermarkStrategy<Long> testWmStrategy) throws Exception {
            int partitionCount = 3;
            TestSourceContext<Long> sourceContext = new TestSourceContext<>();
            TestProcessingTimeService processingTimeService = new TestProcessingTimeService();

            final DummyStreamFetcher<Long> fetcher = DummyStreamFetcher.builder(Long.class)
                    // начальное состояние требуется для корректной работы WatermarkOutputMultiplexer
                    .setSeedPartitionsWithInitialOffsets(initialPartitionOffsets(partitionCount))
                    .setSourceContext(sourceContext)
                    .setProcessingTimeProvider(processingTimeService)
                    .setAutoWatermarkInterval(10)
                    .setWatermarkStrategy(new SerializedValue<>(testWmStrategy))
                    .setPartitionAssigner(new PartitionAssigner(0, 1, partitionCount))
                    .build();

            // elements for partition 0
            final int part0 = 0;
            emitRecord(fetcher, 1L, part0, 1L);
            emitRecord(fetcher, 2L, part0, 2L);
            emitRecord(fetcher, 3L, part0, 3L);
            assertEquals(3L, sourceContext.getLatestElement().getValue().longValue());
            assertEquals(3L, sourceContext.getLatestElement().getTimestamp());

            // elements for partition 1
            final int part1 = 1;
            emitRecord(fetcher, 12L, part1, 1L);
            assertEquals(12L, sourceContext.getLatestElement().getValue().longValue());
            assertEquals(12L, sourceContext.getLatestElement().getTimestamp());

            // elements for partition 2
            final int part2 = 2;
            emitRecord(fetcher, 101L, part2, 1L);
            emitRecord(fetcher, 102L, part2, 2L);
            assertEquals(102L, sourceContext.getLatestElement().getValue().longValue());
            assertEquals(102L, sourceContext.getLatestElement().getTimestamp());

            processingTimeService.setCurrentTime(10);

            // now, we should have a watermark (this blocks until the periodic thread emitted the watermark)
            assertEquals(3L, sourceContext.getLatestWatermark().getTimestamp());

            // advance partition 2
            emitRecord(fetcher, 1003L, part2, 3L);
            emitRecord(fetcher, 1004L, part2, 4L);
            emitRecord(fetcher, 1005L, part2, 5L);
            assertEquals(1005L, sourceContext.getLatestElement().getValue().longValue());
            assertEquals(1005L, sourceContext.getLatestElement().getTimestamp());

            // advance partition 0 beyond partition 1 - this bumps the watermark
            emitRecord(fetcher, 30L, part0, 4L);
            assertEquals(30L, sourceContext.getLatestElement().getValue().longValue());
            assertEquals(30L, sourceContext.getLatestElement().getTimestamp());

            processingTimeService.setCurrentTime(20);

            // this blocks until the periodic thread emitted the watermark
            assertEquals(12L, sourceContext.getLatestWatermark().getTimestamp());

            // advance partition 1 again - this bumps the watermark
            emitRecord(fetcher, 13L, part1, 2L);
            emitRecord(fetcher, 14L, part1, 3L);
            emitRecord(fetcher, 15L, part1, 4L);

            processingTimeService.setCurrentTime(30);
            // this blocks until the periodic thread emitted the watermark
            long watermarkTs = sourceContext.getLatestWatermark().getTimestamp();
            assertTrue(watermarkTs >= 13L && watermarkTs <= 15L);
        }

        @ParameterizedTest
        @Timeout(5)
        @MethodSource("getWatermarkStrategy")
        public void testPeriodicWatermarksWithNoSubscribedPartitionsShouldYieldNoWatermarks(
                WatermarkStrategy<Long> testWmStrategy) throws Exception {
            int partitionCount = 0;
            TestSourceContext<Long> sourceContext = new TestSourceContext<>();
            TestProcessingTimeService processingTimeService = new TestProcessingTimeService();

            final DummyStreamFetcher<Long> fetcher = DummyStreamFetcher.builder(Long.class)
                    .setSourceContext(sourceContext)
                    .setProcessingTimeProvider(processingTimeService)
                    .setAutoWatermarkInterval(10)
                    .setWatermarkStrategy(new SerializedValue<>(testWmStrategy))
                    .setPartitionAssigner(new PartitionAssigner(0, 1, partitionCount))
                    .build();

            processingTimeService.setCurrentTime(10);
            // no partitions; when the periodic watermark emitter fires, no watermark should be emitted
            assertFalse(sourceContext.hasWatermark());
        }

    }

    @Test
    public void testPunctuatedWatermarks() throws Exception {
        int partitionCount = 3;
        TestSourceContext<Long> sourceContext = new TestSourceContext<>();
        TestProcessingTimeService processingTimeService = new TestProcessingTimeService();

        AssignerWithPunctuatedWatermarksAdapter.Strategy<Long> testWmStrategy =
                new AssignerWithPunctuatedWatermarksAdapter.Strategy<>(new PunctuatedTestExtractor());

        final DummyStreamFetcher<Long> fetcher = DummyStreamFetcher.builder(Long.class)
                // начальное состояние требуется для корректной работы WatermarkOutputMultiplexer
                .setSeedPartitionsWithInitialOffsets(initialPartitionOffsets(partitionCount))
                .setSourceContext(sourceContext)
                .setProcessingTimeProvider(processingTimeService)
                .setAutoWatermarkInterval(0)
                .setWatermarkStrategy(new SerializedValue<>(testWmStrategy))
                .setPartitionAssigner(new PartitionAssigner(0, 1, partitionCount))
                .build();

        // elements generate a watermark if the timestamp is a multiple of three

        // elements for partition 0
        final int part0 = 0;
        emitRecord(fetcher, 1L, part0, 1L);
        emitRecord(fetcher, 2L, part0, 2L);
        emitRecord(fetcher, 3L, part0, 3L);
        assertEquals(3L, sourceContext.getLatestElement().getValue().longValue());
        assertEquals(3L, sourceContext.getLatestElement().getTimestamp());
        assertFalse(sourceContext.hasWatermark());

        // elements for partition 1
        final int part1 = 1;
        emitRecord(fetcher, 12L, part1, 1L);
        assertEquals(12L, sourceContext.getLatestElement().getValue().longValue());
        assertEquals(12L, sourceContext.getLatestElement().getTimestamp());
        assertFalse(sourceContext.hasWatermark());

        // elements for partition 2
        final int part2 = 2;
        emitRecord(fetcher, 101L, part2, 1L);
        emitRecord(fetcher, 102L, part2, 2L);
        assertEquals(102L, sourceContext.getLatestElement().getValue().longValue());
        assertEquals(102L, sourceContext.getLatestElement().getTimestamp());

        // now, we should have a watermark
        assertTrue(sourceContext.hasWatermark());
        assertEquals(3L, sourceContext.getLatestWatermark().getTimestamp());

        // advance partition 2
        emitRecord(fetcher, 1003L, part2, 3L);
        emitRecord(fetcher, 1004L, part2, 4L);
        emitRecord(fetcher, 1005L, part2, 5L);
        assertEquals(1005L, sourceContext.getLatestElement().getValue().longValue());
        assertEquals(1005L, sourceContext.getLatestElement().getTimestamp());

        // advance partition 0 beyond partition 1 - this bumps the watermark
        emitRecord(fetcher, 30L, part0, 4L);
        assertEquals(30L, sourceContext.getLatestElement().getValue().longValue());
        assertEquals(30L, sourceContext.getLatestElement().getTimestamp());
        assertTrue(sourceContext.hasWatermark());
        assertEquals(12L, sourceContext.getLatestWatermark().getTimestamp());

        // advance partition 1 again - this bumps the watermark
        emitRecord(fetcher, 13L, part1, 2L);
        assertFalse(sourceContext.hasWatermark());
        emitRecord(fetcher, 14L, part1, 3L);
        assertFalse(sourceContext.hasWatermark());
        emitRecord(fetcher, 15L, part1, 4L);
        assertTrue(sourceContext.hasWatermark());
        assertEquals(15L, sourceContext.getLatestWatermark().getTimestamp());
    }

    private static void emitRecord(DummyStreamFetcher<Long> fetcher, Long record, int partition, long offset) {
        UnpackedMessageData<Long> messageData = new UnpackedMessageData<>(record, offset, Long.MIN_VALUE);
        UnpackedMessageBatch<Long> batch = new UnpackedMessageBatch<>(TOPIC, partition, List.of(messageData));
        fetcher.handleReadResponse(
                "1",
                new UnpackedReadResponse<>(List.of(batch), 100),
                mock(BatchingStreamListener.ReadResponder.class)
        );
    }

    private static Map<TopicPartition, Long> initialPartitionOffsets(int partitionCount) {
        return initialPartitionOffsets(TOPIC, partitionCount);
    }

    private static Map<TopicPartition, Long> initialPartitionOffsets(String topic, int partitionCount) {
        return IntStream.range(0, partitionCount).boxed().collect(Collectors.toMap(
                i -> new TopicPartition(topic, i),
                i -> 0L
        ));
    }

    @SuppressWarnings("deprecation")
    private static class PeriodicTestExtractor implements AssignerWithPeriodicWatermarks<Long> {

        private volatile long maxTimestamp = Long.MIN_VALUE;

        @Override
        public long extractTimestamp(Long element, long previousElementTimestamp) {
            maxTimestamp = Math.max(maxTimestamp, element);
            return element;
        }

        @Nullable
        @Override
        public Watermark getCurrentWatermark() {
            return new Watermark(maxTimestamp);
        }
    }

    @SuppressWarnings("deprecation")
    private static class PunctuatedTestExtractor implements AssignerWithPunctuatedWatermarks<Long> {

        @Override
        public long extractTimestamp(Long element, long previousElementTimestamp) {
            return element;
        }

        @Nullable
        @Override
        public Watermark checkAndGetNextWatermark(Long lastElement, long extractedTimestamp) {
            if (extractedTimestamp % 3 == 0) {
                return new Watermark(extractedTimestamp);
            }
            return null;
        }
    }

    private static class PeriodicTestWatermarkGenerator implements WatermarkGenerator<Long> {

        private volatile long maxTimestamp = Long.MIN_VALUE;

        @Override
        public void onEvent(Long event, long eventTimestamp, WatermarkOutput output) {
            maxTimestamp = Math.max(maxTimestamp, event);
        }

        @Override
        public void onPeriodicEmit(WatermarkOutput output) {
            output.emitWatermark(new org.apache.flink.api.common.eventtime.Watermark(maxTimestamp));
        }
    }
}
