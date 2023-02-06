package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer;

import java.util.List;
import java.util.Set;
import java.util.concurrent.CountDownLatch;

import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.core.testutils.CheckedThread;
import org.apache.flink.runtime.state.StateSnapshotContextSynchronousImpl;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import ru.yandex.taxi.dmp.flink.SerializationTestUtils;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.Installations;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.TestInstallations;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.common.ConfigurationService;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.TopicPartition;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.LongDeserializationSchema;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.TestSourceContext;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.TestingListState;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.any;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.ConsumerUtils.buildTopicResult;
import static ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.ConsumerUtils.setupConsumer;

class FlinkLogbrokerConsumerTest {
    public static final String TOPIC = "dummyTopic";
    public static final String TOPIC_ID = "dummyTopicId";
    public static final String CONSUMER = "dummyConsumer";

    @Test
    @Timeout(5)
    public void testCommon() throws Exception {
        final int partitionCount = 3;

        LogbrokerConsumerConfig config = LogbrokerConsumerConfig
                .builder(TOPIC, CONSUMER)
                .build();

        FlinkLogbrokerConsumer<Long> consumer = spy(new FlinkLogbrokerConsumer<>(
                TestInstallations.TEST, config, new LongDeserializationSchema()
        ));
        TestSourceContext<Long> sourceContext = new TestSourceContext<>();

        final ConsumerUtils.ConsumerHelper consumerHelper = new ConsumerUtils.ConsumerHelper(TOPIC_ID, partitionCount);

        doReturn(consumerHelper.mockConsumer).when(consumer).createLogbrokerConsumer(any());

        ConfigurationService mockConfigurationService = mock(ConfigurationService.class);
        doReturn(mockConfigurationService).when(consumer).createConfigurationService();
        doReturn(buildTopicResult(partitionCount))
                .when(mockConfigurationService)
                .getTopic(any(String.class));

        assertEquals(
                TestInstallations.TEST.configurationEndpoint,
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
        CountDownLatch runLatch = new CountDownLatch(1);
        doAnswer(invocation -> {
            runLatch.countDown();
            return null;
        }).when(consumerHelper.mockConsumer).startConsume(any());
        runThread.start();

        runLatch.await();
        consumerHelper.init();

        // emmit elements for partition 0
        final int part0 = 0;
        consumerHelper.emitRecords(List.of(Tuple2.of(1L, 1L), Tuple2.of(2L, 2L)), part0, 100);
        consumerHelper.emitRecords(List.of(Tuple2.of(3L, 3L)), part0, 101);

        assertEquals(3L, sourceContext.getLatestElement().getValue().longValue());
        assertEquals(3L, sourceContext.getLatestElement().getTimestamp());

        // elements for partition 1
        final int part1 = 1;
        consumerHelper.emitRecords(List.of(Tuple2.of(12L, 1L)), part1, 200L);

        assertEquals(12L, sourceContext.getLatestElement().getValue().longValue());
        assertEquals(12L, sourceContext.getLatestElement().getTimestamp());

        // elements for partition 2
        final int part2 = 2;
        consumerHelper.emitRecords(List.of(Tuple2.of(101L, 1L), Tuple2.of(102L, 2L)), part2, 300L);

        assertEquals(102L, sourceContext.getLatestElement().getValue().longValue());
        assertEquals(102L, sourceContext.getLatestElement().getTimestamp());

        /* checkpoint */
        synchronized (sourceContext.getCheckpointLock()) {
            consumer.snapshotState(new StateSnapshotContextSynchronousImpl(140, 140));
        }
        assertEquals(
                Set.of(
                        Tuple2.of(new TopicPartition(TOPIC_ID, part0), 3L),
                        Tuple2.of(new TopicPartition(TOPIC_ID, part1), 1L),
                        Tuple2.of(new TopicPartition(TOPIC_ID, part2), 2L)),
                Set.copyOf(restoredListState.getList())
        );

        /* commit */
        consumer.notifyCheckpointComplete(140);
        verify(consumerHelper.mockReadResponder, times(1))
                .commit(List.of(100L, 101L, 200L, 300L));

        /* ack commit*/
        consumerHelper.commited(List.of(100L, 101L, 200L, 300L));

        consumer.close();
        runThread.sync();
    }

    @Test
    public void testSerializable() throws Exception {
        LogbrokerConsumerConfig config = LogbrokerConsumerConfig
                .builder(TOPIC, CONSUMER)
                .build();

        FlinkLogbrokerConsumer<String> consumer = new FlinkLogbrokerConsumer<>(
                TestInstallations.TEST, config, new SimpleStringSchema()
        );
        final byte[] bytes = SerializationTestUtils.serialize(consumer);
        @SuppressWarnings("unchecked") final FlinkLogbrokerConsumer<String> deserializeConsumer =
                (FlinkLogbrokerConsumer<String>) SerializationTestUtils.deserialize(bytes);
        assertEquals(deserializeConsumer.getProducedType(), TypeInformation.of(String.class));
    }

    @Test
    public void testSerializableWithCurrentClusterProvider() throws Exception {
        LogbrokerConsumerConfig config = LogbrokerConsumerConfig
                .builder(TOPIC, CONSUMER)
                .build();

        FlinkLogbrokerConsumer<String> consumer = new FlinkLogbrokerConsumer<>(
                Installations.LOGBROKER.currentClusterProvider(), config, new SimpleStringSchema()
        );
        final byte[] bytes = SerializationTestUtils.serialize(consumer);
        @SuppressWarnings("unchecked") final FlinkLogbrokerConsumer<String> deserializeConsumer =
                (FlinkLogbrokerConsumer<String>) SerializationTestUtils.deserialize(bytes);
        assertEquals(deserializeConsumer.getProducedType(), TypeInformation.of(String.class));
    }
}
