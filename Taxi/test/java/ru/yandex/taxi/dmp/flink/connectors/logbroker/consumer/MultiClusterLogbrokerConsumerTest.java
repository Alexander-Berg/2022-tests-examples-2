package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer;

import java.lang.reflect.Field;
import java.util.List;
import java.util.Set;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.CountDownLatch;
import java.util.stream.Stream;

import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.core.testutils.CheckedThread;
import org.apache.flink.runtime.state.StateSnapshotContextSynchronousImpl;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import ru.yandex.kikimr.persqueue.consumer.BatchingStreamConsumer;
import ru.yandex.taxi.dmp.flink.SerializationTestUtils;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.Installations;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.common.ConfigurationService;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.QueueBasedFetcher;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.TopicPartition;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.LongDeserializationSchema;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.TestSourceContext;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.TestingListState;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.ConsumerUtils.ConsumerHelper;
import static ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.ConsumerUtils.buildTopicResult;
import static ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.ConsumerUtils.setupConsumer;

class MultiClusterLogbrokerConsumerTest {
    public static final String TOPIC = "dummyTopic";
    public static final String SAS_TOPIC_ID = "sasTopicId";
    public static final String MYT_TOPIC_ID = "mytTopicId";
    public static final String CONSUMER = "dummyConsumer";

    /*
     * тест может флапать, так как основан на таймаутах
     */
    @Test
    @Timeout(5)
    public void testCommon() throws Exception {
        final int partitionCount = 3;

        LogbrokerConsumerConfig config = LogbrokerConsumerConfig
                .builder(TOPIC, CONSUMER)
                .build();

        MultiClusterLogbrokerConsumer<Long> consumer = spy(new MultiClusterLogbrokerConsumer<>(
                Installations.LOGBROKER,
                Set.of(Installations.LOGBROKER.SAS, Installations.LOGBROKER.MYT),
                config,
                new LongDeserializationSchema()
        ));
        TestSourceContext<Long> sourceContext = new TestSourceContext<>();


        final ConsumerHelper sas = new ConsumerHelper(SAS_TOPIC_ID, partitionCount);
        final ConsumerHelper myt = new ConsumerHelper(MYT_TOPIC_ID, partitionCount);

        List<BatchingStreamConsumer> mockSDKConsumers = List.of(sas.mockConsumer, myt.mockConsumer);
        doReturn(mockSDKConsumers).when(consumer).createLogbrokerConsumer(any());

        ConfigurationService mockConfigurationService = mock(ConfigurationService.class);
        doReturn(mockConfigurationService).when(consumer).createConfigurationService();
        doReturn(buildTopicResult(partitionCount))
                .when(mockConfigurationService)
                .getTopic(any(String.class));

        assertEquals(
                Installations.LOGBROKER.configurationEndpoint,
                consumer.getConfigurationEndpoint()
        );
        final TestingListState<Tuple2<TopicPartition, Long>> restoredListState = new TestingListState<>();

        setupConsumer(consumer,
                true,
                restoredListState,
                true,
                0,
                1
        );
        CheckedThread runThread = new CheckedThread() {
            @Override
            public void go() throws Exception {
                consumer.run(sourceContext);
            }
        };
        CountDownLatch runLatch = new CountDownLatch(2);

        doAnswer(invocation -> {
            runLatch.countDown();
            return null;
        }).when(sas.mockConsumer).startConsume(any());

        doAnswer(invocation -> {
            runLatch.countDown();
            return null;
        }).when(myt.mockConsumer).startConsume(any());

        runThread.start();

        runLatch.await();

        Stream.of(sas, myt).forEach(ConsumerHelper::init);
        // хак, чтобы дождаться обработки данных в параллельном потоке
        BlockingQueue<?> queue = getFetchQueue(consumer);

        // emmit elements for partition 0
        final int part0 = 0;
        sas.emitRecords(List.of(Tuple2.of(1L, 1L), Tuple2.of(2L, 2L)), part0, 100);
        myt.emitRecords(List.of(Tuple2.of(3L, 3L)), part0, 101);
        sas.emitRecords(List.of(Tuple2.of(4L, 4L)), part0, 102);
        waitEmptyQueue(queue);

        assertEquals(4L, sourceContext.getLatestElement().getValue().longValue());
        assertEquals(4L, sourceContext.getLatestElement().getTimestamp());

        // elements for partition 1
        final int part1 = 1;
        sas.emitRecords(List.of(Tuple2.of(12L, 1L)), part1, 200L);
        waitEmptyQueue(queue);

        assertEquals(12L, sourceContext.getLatestElement().getValue().longValue());
        assertEquals(12L, sourceContext.getLatestElement().getTimestamp());

        // elements for partition 2
        final int part2 = 2;
        myt.emitRecords(List.of(Tuple2.of(101L, 1L), Tuple2.of(102L, 2L)), part2, 300L);
        waitEmptyQueue(queue);

        assertEquals(102L, sourceContext.getLatestElement().getValue().longValue());
        assertEquals(102L, sourceContext.getLatestElement().getTimestamp());

        /* checkpoint */
        synchronized (sourceContext.getCheckpointLock()) {
            consumer.snapshotState(new StateSnapshotContextSynchronousImpl(140, 140));
        }
        assertEquals(
                Set.of(
                        Tuple2.of(new TopicPartition(sas.topicId, part0), 4L),
                        Tuple2.of(new TopicPartition(sas.topicId, part1), 1L),
                        Tuple2.of(new TopicPartition(sas.topicId, part2), Long.MIN_VALUE),
                        Tuple2.of(new TopicPartition(myt.topicId, part0), 3L),
                        Tuple2.of(new TopicPartition(myt.topicId, part1), Long.MIN_VALUE),
                        Tuple2.of(new TopicPartition(myt.topicId, part2), 2L)
                ),
                Set.copyOf(restoredListState.getList())
        );

        /* commit */
        consumer.notifyCheckpointComplete(140);
        final List<Long> sasCookies = List.of(100L, 102L, 200L);
        verify(sas.mockReadResponder, times(1)).commit(sasCookies);
        final List<Long> mytCookies = List.of(101L, 300L);
        verify(myt.mockReadResponder, times(1)).commit(mytCookies);

        /* ack commit*/
        sas.commited(sasCookies);
        myt.commited(mytCookies);

        consumer.close();
        runThread.sync();
    }

    private BlockingQueue<?> getFetchQueue(MultiClusterLogbrokerConsumer<Long> consumer) throws Exception {
        Field fetcherField = BaseLogbrokerConsumer.class.getDeclaredField("fetcher");
        fetcherField.setAccessible(true);
        final Field messageQueueField = QueueBasedFetcher.class.getDeclaredField("messageQueue");
        messageQueueField.setAccessible(true);
        QueueBasedFetcher<Long> fetcher = (QueueBasedFetcher<Long>) fetcherField.get(consumer);
        final BlockingQueue<?> queue = (BlockingQueue<?>) messageQueueField.get(fetcher);
        fetcherField.setAccessible(false);
        messageQueueField.setAccessible(false);
        return queue;
    }

    private void waitEmptyQueue(BlockingQueue<?> queue) throws Exception {
        while (!queue.isEmpty()) {
            Thread.sleep(10);
        }
        // нужно дать время на обработку последней записи
        Thread.sleep(20);
    }

    @Test
    public void testSerializable() throws Exception {
        LogbrokerConsumerConfig config = LogbrokerConsumerConfig
                .builder(TOPIC, CONSUMER)
                .build();

        MultiClusterLogbrokerConsumer<String> consumer = spy(new MultiClusterLogbrokerConsumer<>(
                Installations.LOGBROKER,
                Set.of(Installations.LOGBROKER.SAS, Installations.LOGBROKER.MYT),
                config,
                new SimpleStringSchema()
        ));
        final byte[] bytes = SerializationTestUtils.serialize(consumer);
        @SuppressWarnings("unchecked") final MultiClusterLogbrokerConsumer<String> deserializeConsumer =
                (MultiClusterLogbrokerConsumer<String>) SerializationTestUtils.deserialize(bytes);
        assertEquals(deserializeConsumer.getProducedType(), TypeInformation.of(String.class));
    }
}
