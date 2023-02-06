package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer;

import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.ListIterator;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import com.google.common.collect.Lists;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.runtime.state.StateSnapshotContextSynchronousImpl;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.streaming.util.MockDeserializationSchema;
import org.apache.flink.util.ExceptionUtils;
import org.apache.flink.util.function.ThrowingConsumer;
import org.junit.Assert;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.mockito.ArgumentCaptor;

import ru.yandex.taxi.dmp.flink.connectors.logbroker.Installation;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.ThreadTestUtils;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.common.ConfigurationService;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.BaseStreamFetcher;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.TopicPartition;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.TestingListState;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;
import static org.mockito.Mockito.any;
import static org.mockito.Mockito.anyLong;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static ru.yandex.taxi.dmp.flink.connectors.logbroker.ThreadTestUtils.testBlockedMethodLifecycle;
import static ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.ConsumerUtils.buildTopicResult;
import static ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.ConsumerUtils.setupConsumer;

class BaseLogbrokerConsumerTest {
    public static final String TOPIC = "dummyTopic";
    public static final String CONSUMER = "dummyConsumer";
    public static final LogbrokerConsumerConfig TEST_CONFIG = LogbrokerConsumerConfig.builder(TOPIC, CONSUMER).build();
    public static final LogbrokerConsumerConfig OBSERVER_CONFIG = LogbrokerConsumerConfig.builder(TOPIC, CONSUMER)
            // запускаем observer чаще, чтобы у теста было приемлемое время выполнения
            .setObservedPartitionsDelayMilli(100)
            .build();

    @Test
    public void testCheckpointRequired() throws Exception {
        final DummyLogbrokerConsumer<String> consumer = new DummyLogbrokerConsumer<>();

        try {
            setupConsumer(
                    consumer,
                    false,
                    null,
                    false,
                    0,
                    1
            );

            fail();
        } catch (FlinkLogbrokerException e) {
            assertEquals(
                    "Consumer is not allowed without checkpoint",
                    e.getMessage()
            );
        }
    }

    @Test
    @Timeout(5)
    public void testOpenBlocked() throws Exception {
        MockDeserializationSchema<String> deserializationSchema = new MockDeserializationSchema<>();
        final DummyLogbrokerConsumer<String> consumer =
                new DummyLogbrokerConsumer<>(TEST_CONFIG, deserializationSchema);

        testBlockedMethodLifecycle(
                consumer,
                ConsumerUtils::initConsumer,
                consumer_ -> consumer_.open(new Configuration()),
                c -> {
                }
        );
        // В рамках consumer.open() должен быть обязательно вызван deserializationSchema.open()
        assertTrue(deserializationSchema.isOpenCalled());
    }

    @Test
    @Timeout(5)
    public void testCloseBlocked() throws Exception {
        testBlockedMethod(ConsumerUtils::setupConsumer, BaseLogbrokerConsumer::close);
    }

    @Test
    @Timeout(5)
    public void testCloseBeforeRunning() throws Exception {
        DummyLogbrokerConsumer<String> consumer = testBlockedMethod(
                ConsumerUtils::setupConsumer,
                consumer_ -> consumer_.run(mock(SourceFunction.SourceContext.class)),
                BaseLogbrokerConsumer::close
        );

        assertNull(consumer.getObservedPartitionsFuture());
        verify(consumer.mockFetcher, never()).runFetchLoop();
        verify(consumer.mockFetcher, never()).cancel();
        verify(consumer.mockConfigurationService).close();
    }

    @Test
    @Timeout(5)
    public void testCloseAfterRunning() throws Exception {
        DummyLogbrokerConsumer<String> consumer = testBlockedMethod(
                ConsumerUtils::setupConsumer,
                BaseLogbrokerConsumer::close,
                consumer_ -> consumer_.run(mock(SourceFunction.SourceContext.class))
        );

        // был вызван run()
        assertNotNull(consumer.getObservedPartitionsFuture());
        verify(consumer.mockFetcher, times(1)).runFetchLoop();
        // был вызван cancel()
        assertTrue(consumer.observedPartitionsScheduledFuture.isCancelled());
        verify(consumer.mockFetcher).cancel();
        verify(consumer.mockConfigurationService).close();
    }

    @Test
    @Timeout(5)
    public void testObservedNewPartition() throws Exception {
        MockDeserializationSchema<String> deserializationSchema = new MockDeserializationSchema<>();
        final DummyLogbrokerConsumer<String> consumer =
                new DummyLogbrokerConsumer<>(OBSERVER_CONFIG, deserializationSchema);

        setupConsumer(consumer);
        consumer.run(mock(SourceFunction.SourceContext.class));
        consumer.setPartitionCount(2);
        // должно быть брошено исключение, так как изменилось кол-во партиций
        Throwable observedPartitionsException = null;
        try {
            consumer.getObservedPartitionsFuture().get();
        } catch (ExecutionException e) {
            observedPartitionsException = e.getCause();
        }
        consumer.close();

        assertNotNull(observedPartitionsException);
        assertTrue(observedPartitionsException instanceof NonAssignedPartitionException);

        // исключение не должно помешать корректно закрыть consumer
        verify(consumer.mockFetcher).cancel();
        verify(consumer.mockConfigurationService).close();
    }

    @Test
    @Timeout(5)
    public void testPartitionObserverError() throws Exception {
        MockDeserializationSchema<String> deserializationSchema = new MockDeserializationSchema<>();
        final DummyLogbrokerConsumer<String> consumer =
                new DummyLogbrokerConsumer<>(OBSERVER_CONFIG, deserializationSchema);

        Exception failCause = new RuntimeException("test");

        doAnswer(inv -> {
            doThrow(failCause).when(consumer.mockConfigurationService).getTopic(any(String.class));
            consumer.getObservedPartitionsFuture().get();
            return null;
        }).when(
                consumer.mockFetcher
        ).runFetchLoop();

        testFailingConsumerLifecycle(consumer, failCause);

        // исключение не должно помешать корректно закрыть consumer
        verify(consumer.mockFetcher).cancel();
        verify(consumer.mockConfigurationService).close();
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testSnapshotStateWithCommitOnCheckpointsEnabled() throws Exception {

        final List<Tuple2<TopicPartition, Long>> state1 = List.of(
                Tuple2.of(new TopicPartition("abc", 0), 16768L),
                Tuple2.of(new TopicPartition("def", 1), 987654321L)
        );

        final List<Tuple2<TopicPartition, Long>> state2 = List.of(
                Tuple2.of(new TopicPartition("abc", 0), 16770L),
                Tuple2.of(new TopicPartition("def", 1), 987654329L)
        );

        final List<Tuple2<TopicPartition, Long>> state3 = List.of(
                Tuple2.of(new TopicPartition("abc", 0), 16780L),
                Tuple2.of(new TopicPartition("def", 1), 987654377L)
        );
        // --------------------------------------------------------------------

        final DummyLogbrokerConsumer<String> consumer = new DummyLogbrokerConsumer<>();
        consumer.setPartitionCount(2);

        final TestingListState<Tuple2<TopicPartition, Long>> listState = new TestingListState<>();

        // setup and run the consumer; wait until the consumer reaches the main fetch loop before continuing test
        setupConsumer(consumer, false, listState, true, 0, 1);

        consumer.run(mock(SourceFunction.SourceContext.class));

        doReturn(state1, state2, state3).when(consumer.mockFetcher).snapshotCurrentState(anyLong());

        // checkpoint 1
        consumer.snapshotState(new StateSnapshotContextSynchronousImpl(138, 138));
        assertEquals(state1, toList(listState));

        // checkpoint 2
        consumer.snapshotState(new StateSnapshotContextSynchronousImpl(140, 140));
        assertEquals(state2, toList(listState));

        ArgumentCaptor<Long> captor = ArgumentCaptor.forClass(Long.class);

        // ack checkpoint 1
        consumer.notifyCheckpointComplete(138L);
        verify(consumer.mockFetcher).commitLogbrokerCookies(captor.capture());
        assertEquals(Long.valueOf(138L), captor.getValue());

        // checkpoint 3
        consumer.snapshotState(new StateSnapshotContextSynchronousImpl(141, 141));
        assertEquals(state3, toList(listState));

        // ack checkpoint 2
        consumer.notifyCheckpointComplete(140L);
        verify(consumer.mockFetcher, times(2)).commitLogbrokerCookies(captor.capture());
        assertEquals(Long.valueOf(140L), captor.getValue());

        consumer.cancel();
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testSnapshotStateBeforeRun() throws Exception {
        final List<Tuple2<TopicPartition, Long>> state1 = List.of(
                Tuple2.of(new TopicPartition("abc", 0), 16768L),
                Tuple2.of(new TopicPartition("def", 1), 987654321L)
        );

        final List<Tuple2<TopicPartition, Long>> state2 = List.of(
                Tuple2.of(new TopicPartition("abc", 0), 16770L),
                Tuple2.of(new TopicPartition("def", 1), 987654329L)
        );

        // --------------------------------------------------------------------

        final DummyLogbrokerConsumer<String> consumer = new DummyLogbrokerConsumer<>();
        consumer.setPartitionCount(2);

        final TestingListState<Tuple2<TopicPartition, Long>> listState = new TestingListState<>();
        listState.addAll(state1);

        // setup and run the consumer; wait until the consumer reaches the main fetch loop before continuing test
        setupConsumer(consumer, true, listState, true, 0, 1);

        // checkpoint 1
        consumer.snapshotState(new StateSnapshotContextSynchronousImpl(138, 138));
        assertEquals(state1, toList(listState));
        Assert.assertTrue(listState.isClearCalled());

        // run
        consumer.run(mock(SourceFunction.SourceContext.class));

        // checkpoint 2
        doReturn(state2).when(consumer.mockFetcher).snapshotCurrentState(anyLong());
        consumer.snapshotState(new StateSnapshotContextSynchronousImpl(140, 140));
        assertEquals(state2, toList(listState));

        ArgumentCaptor<Long> captor = ArgumentCaptor.forClass(Long.class);

        // ack checkpoint 1
        consumer.notifyCheckpointComplete(138L);
        verify(consumer.mockFetcher).commitLogbrokerCookies(captor.capture());
        assertEquals(Long.valueOf(138L), captor.getValue());

        consumer.cancel();
    }

    private static List<Tuple2<TopicPartition, Long>> toList(
            TestingListState<Tuple2<TopicPartition, Long>> listState
    ) throws Exception {
        final List<Tuple2<TopicPartition, Long>> snapshot = Lists.newArrayList(listState.get());
        snapshot.sort(Comparator.comparingInt(o -> o.f0.getPartition()));
        return snapshot;
    }

    private <T> void testFailingConsumerLifecycle(BaseLogbrokerConsumer<T> consumer,
                                                  Exception expectedException) throws Exception {
        try {
            setupConsumer(consumer);
            consumer.run(mock(SourceFunction.SourceContext.class));
            fail("Exception should have been thrown from open / run method of consumer.");
        } catch (Exception e) {
            assertTrue(ExceptionUtils.findThrowable(e, throwable -> throwable.equals(expectedException)).isPresent());
        }
        consumer.close();
    }

    public DummyLogbrokerConsumer<String> testBlockedMethod(
            ThrowingConsumer<DummyLogbrokerConsumer<String>, Exception> init,
            ThrowingConsumer<DummyLogbrokerConsumer<String>, Exception> blockedMethod
    ) throws Exception {
        return testBlockedMethod(init, blockedMethod, c -> {
        });
    }

    public DummyLogbrokerConsumer<String> testBlockedMethod(
            ThrowingConsumer<DummyLogbrokerConsumer<String>, Exception> init,
            ThrowingConsumer<DummyLogbrokerConsumer<String>, Exception> blockedMethod,
            ThrowingConsumer<DummyLogbrokerConsumer<String>, Exception> onBlock
    ) throws Exception {
        final DummyLogbrokerConsumer<String> consumer = new DummyLogbrokerConsumer<>();

        testBlockedMethodLifecycle(consumer, init, blockedMethod, onBlock);

        return consumer;
    }

    @Test
    public void testOpenWithRestoreState() throws Exception {
        MockDeserializationSchema<String> deserializationSchema = new MockDeserializationSchema<>();
        final DummyLogbrokerConsumer<String> consumer =
                new DummyLogbrokerConsumer<>(TEST_CONFIG, deserializationSchema);

        final TestingListState<Tuple2<TopicPartition, Long>> restoredListState = new TestingListState<>();
        setupConsumer(consumer, true, restoredListState, true, 0, 1);

        assertTrue(deserializationSchema.isOpenCalled());
    }

    @Test
    public void testNonAssignedPartitions() throws Exception {
        // single subtask
        checkPartitionAssignment(0, List.of(Collections.emptyMap()));
        // two subtask
        checkPartitionAssignment(0, List.of(Collections.emptyMap(), Collections.emptyMap()));
    }

    @Test
    public void testAssignedPartitionsOnSingleTask() throws Exception {
        checkPartitionAssignment(1, List.of(expectedPartitions(0)));
        checkPartitionAssignment(2, List.of(expectedPartitions(0, 1)));
    }

    @Test
    public void testAssignedPartitionsOnMultiTasks() throws Exception {
        checkPartitionAssignment(1, List.of(expectedPartitions(0), Collections.emptyMap()));
        checkPartitionAssignment(2, List.of(expectedPartitions(0), expectedPartitions(1)));
        checkPartitionAssignment(
                2, List.of(expectedPartitions(0), expectedPartitions(1), Collections.emptyMap()));
        checkPartitionAssignment(3, List.of(expectedPartitions(0, 2), expectedPartitions(1)));
        checkPartitionAssignment(
                3, List.of(expectedPartitions(0), expectedPartitions(1), expectedPartitions(2)));
    }

    public void checkPartitionAssignment(int restoredSize,
                                         List<Map<TopicPartition, Long>> expectedPartitions) throws Exception {
        ListIterator<Map<TopicPartition, Long>> it = expectedPartitions.listIterator();
        int totalSubtasks = expectedPartitions.size();
        while (it.hasNext()) {
            int subtaskIndex = it.nextIndex();
            final Map<TopicPartition, Long> expected = it.next();

            final DummyLogbrokerConsumer<String> consumer = new DummyLogbrokerConsumer<>();
            consumer.setPartitionCount(restoredSize);
            final TestingListState<Tuple2<TopicPartition, Long>> restoredListState = new TestingListState<>();
            restoredListState.addAll(restoredState(restoredSize));

            setupConsumer(consumer, true, restoredListState, true, subtaskIndex, totalSubtasks);
            assertEquals(expected, consumer.getPartitionsToStartOffsets());
        }
    }

    private List<Tuple2<TopicPartition, Long>> restoredState(int size) {
        return IntStream.range(0, size)
                .mapToObj(this::partitionToState)
                .collect(Collectors.toList());
    }

    private Tuple2<TopicPartition, Long> partitionToState(int i) {
        return Tuple2.of(new TopicPartition(TOPIC, i), i * 10L);
    }

    private Map<TopicPartition, Long> expectedPartitions(int... partitions) {
        return Arrays.stream(partitions)
                .mapToObj(this::partitionToState)
                .collect(Collectors.toMap(t -> t.f0, t -> t.f1));
    }

    // ------------------------------------------------------------------------

    static class DummyLogbrokerConsumer<T>
            extends BaseLogbrokerConsumer<T>
            implements ThreadTestUtils.BlockedClosable {
        volatile CompletableFuture<?> observedPartitionsFuture;
        private final BaseStreamFetcher<T> mockFetcher = mock(BaseStreamFetcher.class);
        private final ConfigurationService mockConfigurationService = mock(ConfigurationService.class);

        DummyLogbrokerConsumer() {
            this(TEST_CONFIG, new MockDeserializationSchema<>());
        }

        DummyLogbrokerConsumer(LogbrokerConsumerConfig consumerConfig, DeserializationSchema<T> deserializer) {
            super(consumerConfig, deserializer);
            setPartitionCount(1);
        }

        public void setPartitionCount(int partitionCount) {
            doReturn(buildTopicResult(partitionCount))
                    .when(mockConfigurationService)
                    .getTopic(any(String.class));
        }

        public Map<TopicPartition, Long> getPartitionsToStartOffsets() {
            return this.partitionsToStartOffsets;
        }

        public Future<?> getObservedPartitionsFuture() {
            return this.observedPartitionsFuture;
        }

        public boolean isRunning() {
            return this.running.get();
        }

        @Override
        protected BaseStreamFetcher<T> createFetcher(SourceContext<T> sourceContext,
                                                     CompletableFuture<?> observedPartitionsFuture) {
            this.observedPartitionsFuture = observedPartitionsFuture;
            return mockFetcher;
        }

        @Override
        protected Installation.Endpoint getConfigurationEndpoint() {
            return null;
        }

        @Override
        protected ConfigurationService createConfigurationService() {
            return mockConfigurationService;
        }

        @Override
        public void blockByTest(Callable<Void> callable) throws Exception {
            this.runningLock.writeLock().lock();
            callable.call();
            this.runningLock.writeLock().unlock();
        }

        @Override
        public Thread.State getBlockedThreadState() {
            return Thread.State.WAITING;
        }
    }
}
