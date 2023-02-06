package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CompletableFuture;

import com.google.common.primitives.Longs;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.core.testutils.CheckedThread;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.util.ExceptionUtils;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import ru.yandex.kikimr.persqueue.consumer.BatchingStreamConsumer;
import ru.yandex.kikimr.persqueue.consumer.BatchingStreamListener;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerReadResponse;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageBatch;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageData;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.FlinkLogbrokerException;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.message.UnpackedMessageBatch;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.message.UnpackedMessageData;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.message.UnpackedReadResponse;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.DummyStreamFetcher;
import ru.yandex.taxi.dmp.flink.serialization.EventTimestampEntity;

import static java.lang.Thread.State.BLOCKED;
import static java.lang.Thread.State.WAITING;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;
import static org.mockito.Mockito.any;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static ru.yandex.taxi.dmp.flink.connectors.logbroker.ThreadTestUtils.testBlockedMethodLifecycle;
import static ru.yandex.taxi.dmp.flink.connectors.logbroker.ThreadTestUtils.waitNonTerminatedState;
import static ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.MessageFactory.createMessageBatch;
import static ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.MessageFactory.createTestMessageMeta;
import static ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.MessageFactory.createUnpackedBatch;

class BaseStreamFetcherTest {
    public static final String TOPIC = "dummy";

    @Test
    @Timeout(5)
    public void testCloseSynchronized() throws Exception {
        DummyStreamFetcher<String> fetcher = DummyStreamFetcher.builder(String.class).build();

        testBlockedMethodLifecycle(
                fetcher,
                f -> {
                },
                DummyStreamFetcher::close,
                f -> {
                }
        );
    }

    @Test
    @Timeout(5)
    public void testCloseBeforeRunning() throws Exception {
        DummyStreamFetcher<String> spyFetcher = spy(DummyStreamFetcher.builder(String.class).build());
        doReturn(mock(Supervisor.class)).when(spyFetcher).startConsume(any());

        // если runFetchLoop синхронизирован, то выполнится после close и ничего не запустит
        testBlockedMethodLifecycle(
                spyFetcher,
                f -> {
                },
                DummyStreamFetcher::runFetchLoop,
                DummyStreamFetcher::close
        );
        verify(spyFetcher, never()).startConsume(any());
        assertNull(spyFetcher.getSupervisor());
    }

    @Test
    @Timeout(5)
    public void testCloseAfterIdleRunning() throws Exception {
        final int partitionCount = 0;
        SourceFunction.SourceContext<String> sourceContext = mock(SourceFunction.SourceContext.class);
        DummyStreamFetcher<String> spyFetcher = spy(
                DummyStreamFetcher.builder(String.class)
                        .setSourceContext(sourceContext)
                        .setPartitionAssigner(new PartitionAssigner(0, 1, partitionCount))
                        .build()
        );
        doReturn(mock(Supervisor.class)).when(spyFetcher).startConsume(any());

        CheckedThread runFetchThread = new CheckedThread() {
            @Override
            public void go() throws Exception {
                spyFetcher.runFetchLoop();
            }
        };
        runFetchThread.start();

        // runFetchThread должен перейти в ожидание вызова cancel()
        waitNonTerminatedState(runFetchThread, WAITING);

        assertTrue(spyFetcher.isRunning());
        verify(spyFetcher, never()).startConsume(any());
        assertTrue(spyFetcher.getSupervisor() instanceof IdleSupervisor);
        verify(sourceContext, times(1)).markAsTemporarilyIdle();

        spyFetcher.cancel();
        assertFalse(spyFetcher.isRunning());

        // после cancel() поток runFetchThread должен завершиться без ошибок
        runFetchThread.sync();
    }

    @Test
    @Timeout(5)
    public void testCloseAfterConsumeRunning() throws Exception {
        final int partitionCount = 1;
        DummyStreamFetcher<String> spyFetcher = spy(
                DummyStreamFetcher.builder(String.class)
                        .setPartitionAssigner(new PartitionAssigner(0, 1, partitionCount))
                        .build()
        );

        doReturn(new StreamSupervisor(mock(BatchingStreamConsumer.class))).when(spyFetcher).startConsume(any());

        CheckedThread runFetchThread = new CheckedThread() {
            @Override
            public void go() throws Exception {
                spyFetcher.runFetchLoop();
            }
        };
        runFetchThread.start();

        // runFetchThread должен перейти в ожидание вызова cancel()
        waitNonTerminatedState(runFetchThread, WAITING);

        assertTrue(spyFetcher.isRunning());
        // в отличии от idle должен быть вызван startConsume
        verify(spyFetcher, times(1)).startConsume(any());
        assertTrue(spyFetcher.getSupervisor() instanceof StreamSupervisor);

        spyFetcher.cancel();
        assertFalse(spyFetcher.isRunning());

        // после cancel() поток runFetchThread должен завершиться без ошибок
        runFetchThread.sync();
    }

    @Test
    @Timeout(5)
    public void testPartitionObserverErrorWithIdleRunning() throws Exception {
        final int partitionCount = 0;
        final CompletableFuture<Void> partitionObserver = new CompletableFuture<>();
        final Throwable failCause = new RuntimeException("test");

        DummyStreamFetcher<String> spyFetcher = spy(
                DummyStreamFetcher.builder(String.class)
                        .setPartitionAssigner(new PartitionAssigner(0, 1, partitionCount))
                        .setObservedNewPartitionsFuture(partitionObserver)
                        .build()
        );
        doReturn(mock(Supervisor.class)).when(spyFetcher).startConsume(any());

        CheckedThread runFetchThread = new CheckedThread() {
            @Override
            public void go() throws Exception {
                spyFetcher.runFetchLoop();
            }
        };
        runFetchThread.start();

        // runFetchThread должен перейти в ожидание вызова cancel()
        waitNonTerminatedState(runFetchThread, WAITING);

        partitionObserver.completeExceptionally(failCause);

        try {
            runFetchThread.sync();
            fail("no exception");
        } catch (Exception e) {
            assertTrue(ExceptionUtils.findThrowable(e, throwable -> throwable.equals(failCause)).isPresent());
        }
    }

    @Test
    @Timeout(5)
    public void testPartitionObserverErrorWithConsumeRunning() throws Exception {
        final int partitionCount = 1;
        final CompletableFuture<Void> partitionObserver = new CompletableFuture<>();
        final Throwable failCause = new RuntimeException("test");

        DummyStreamFetcher<String> spyFetcher = spy(
                DummyStreamFetcher.builder(String.class)
                        .setPartitionAssigner(new PartitionAssigner(0, 1, partitionCount))
                        .setObservedNewPartitionsFuture(partitionObserver)
                        .build()
        );
        doReturn(new StreamSupervisor(mock(BatchingStreamConsumer.class))).when(spyFetcher).startConsume(any());

        CheckedThread runFetchThread = new CheckedThread() {
            @Override
            public void go() throws Exception {
                spyFetcher.runFetchLoop();
            }
        };
        runFetchThread.start();

        // runFetchThread должен перейти в ожидание вызова cancel()
        waitNonTerminatedState(runFetchThread, WAITING);

        partitionObserver.completeExceptionally(failCause);

        try {
            runFetchThread.sync();
            fail("no exception");
        } catch (Exception e) {
            assertTrue(ExceptionUtils.findThrowable(e, throwable -> throwable.equals(failCause)).isPresent());
        }
    }

    @Test
    public void testUnpackEmptyBatch() throws Exception {
        final DummyStreamFetcher<String> fetcher = DummyStreamFetcher.<String>builder()
                .setDeserializer(new TestDeserializationSchema())
                .build();
        final UnpackedReadResponse<String> result = fetcher.unpack(
                new ConsumerReadResponse(Collections.emptyList(), 1)
        );
        final UnpackedReadResponse<String> expected = new UnpackedReadResponse<>(
                Collections.emptyList(), 1
        );
        assertEquals(expected, result);
    }

    @Test
    public void testUnpackEmptyMessageData() throws Exception {
        final DummyStreamFetcher<String> fetcher = DummyStreamFetcher.<String>builder()
                .setDeserializer(new TestDeserializationSchema())
                .build();


        final UnpackedReadResponse<String> result = fetcher.unpack(
                new ConsumerReadResponse(
                        new ArrayList<>(List.of(new MessageBatch(TOPIC, 0, Collections.emptyList()))),
                        1
                )
        );
        final UnpackedReadResponse<String> expected = new UnpackedReadResponse<>(
                List.of(new UnpackedMessageBatch<>(TOPIC, 0, Collections.emptyList())),
                1
        );
        assertEquals(expected, result);
    }

    @Test
    public void testUnpackSingleMessageData() throws Exception {
        final DummyStreamFetcher<String> fetcher = DummyStreamFetcher.<String>builder()
                .setDeserializer(new TestDeserializationSchema())
                .build();


        final UnpackedReadResponse<String> result = fetcher.unpack(
                new ConsumerReadResponse(
                        new ArrayList<>(List.of(createMessageBatch(TOPIC, 1))),
                        1
                )
        );
        final UnpackedReadResponse<String> expected = new UnpackedReadResponse<>(
                List.of(createUnpackedBatch(TOPIC, 1)),
                1
        );
        assertEquals(expected, result);
    }

    @Test
    public void testUnpackMultiMessageData() throws Exception {
        final DummyStreamFetcher<String> fetcher = DummyStreamFetcher.<String>builder()
                .setDeserializer(new TestDeserializationSchema())
                .build();

        final UnpackedReadResponse<String> result = fetcher.unpack(
                new ConsumerReadResponse(
                        new ArrayList<>(List.of(
                                createMessageBatch("batch1", 2), createMessageBatch("batch2", 4))),
                        1
                )
        );
        final UnpackedReadResponse<String> expected = new UnpackedReadResponse<>(
                List.of(createUnpackedBatch("batch1", 2), createUnpackedBatch("batch2", 4)),
                1
        );
        assertEquals(expected, result);
    }

    public static class TestDeserializationSchema implements DeserializationSchema<String> {
        @Override
        public String deserialize(byte[] message) throws IOException {
            return "test_" + new String(message, StandardCharsets.UTF_8);
        }

        @Override
        public boolean isEndOfStream(String nextElement) {
            return false;
        }

        @Override
        public TypeInformation<String> getProducedType() {
            return TypeInformation.of(String.class);
        }
    }

    @Test
    public void unpackEventTimestampEntity() throws Exception {
        final DummyStreamFetcher<TestEventTimestampEntity> fetcher =
                DummyStreamFetcher.<TestEventTimestampEntity>builder()
                        .setDeserializer(new TestEntityDeserializationSchema())
                        .build();

        final UnpackedReadResponse<TestEventTimestampEntity> result = fetcher.unpack(
                new ConsumerReadResponse(
                        new ArrayList<>(List.of(new MessageBatch(
                                TOPIC,
                                0,
                                new ArrayList<>(List.of(new MessageData(
                                        Longs.toByteArray(1234L),
                                        10,
                                        createTestMessageMeta(100)
                                )))
                        ))),
                        1
                )
        );
        final UnpackedReadResponse<TestEventTimestampEntity> expected = new UnpackedReadResponse<>(
                List.of(new UnpackedMessageBatch<>(
                        TOPIC,
                        0,
                        List.of(new UnpackedMessageData<>(
                                new TestEventTimestampEntity(1234L), 10, 100L
                        ))
                )),
                1
        );
        assertEquals(expected, result);
    }

    private static class TestEventTimestampEntity implements EventTimestampEntity {

        long eventTimestamp;

        private TestEventTimestampEntity(long eventTimestamp) {
            this.eventTimestamp = eventTimestamp;
        }

        @Override
        public long getEventTimestamp() {
            return eventTimestamp;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) {
                return true;
            }
            if (!(o instanceof TestEventTimestampEntity)) {
                return false;
            }

            TestEventTimestampEntity that = (TestEventTimestampEntity) o;

            return eventTimestamp == that.eventTimestamp;
        }

        @Override
        public int hashCode() {
            return (int) (eventTimestamp ^ (eventTimestamp >>> 32));
        }
    }

    public static class TestEntityDeserializationSchema implements DeserializationSchema<TestEventTimestampEntity> {
        @Override
        public TestEventTimestampEntity deserialize(byte[] message) throws IOException {
            return new TestEventTimestampEntity(Longs.fromByteArray(message));
        }

        @Override
        public boolean isEndOfStream(TestEventTimestampEntity nextElement) {
            return false;
        }

        @Override
        public TypeInformation<TestEventTimestampEntity> getProducedType() {
            return TypeInformation.of(TestEventTimestampEntity.class);
        }
    }

    @Test
    public void testHandleReadResponseCheckpointLock() throws Exception {
        Object checkpointLock = new Object();
        SourceFunction.SourceContext<String> sourceContext = mock(SourceFunction.SourceContext.class);
        doReturn(checkpointLock).when(sourceContext).getCheckpointLock();

        final DummyStreamFetcher<String> fetcher = DummyStreamFetcher.builder(String.class)
                .setSourceContext(sourceContext)
                .build();

        CheckedThread thread = new CheckedThread() {
            @Override
            public void go() throws Exception {
                try {
                    fetcher.handleReadResponse(
                            "1",
                            new UnpackedReadResponse<>(
                                    List.of(createUnpackedBatch(TOPIC, 1)),
                                    100
                            ),
                            mock(BatchingStreamListener.ReadResponder.class)
                    );
                } catch (Exception e) {
                    // иначе может казаться, что тест упал без видимых причин
                    e.printStackTrace();
                }
            }
        };

        synchronized (checkpointLock) {
            thread.start();
            waitNonTerminatedState(thread, BLOCKED);
        }
        thread.sync();
    }

    @Test
    @Timeout(5)
    public void testProcessing() throws Exception {
        Object checkpointLock = new Object();
        SourceFunction.SourceContext<String> sourceContext = mock(SourceFunction.SourceContext.class);
        doReturn(checkpointLock).when(sourceContext).getCheckpointLock();

        int partitionCount = 2;
        final DummyStreamFetcher<String> fetcher = DummyStreamFetcher.builder(String.class)
                .setPartitionAssigner(new PartitionAssigner(0, 1, partitionCount))
                .setSourceContext(sourceContext)
                .build();

        final BatchingStreamListener.ReadResponder readResponder = mock(BatchingStreamListener.ReadResponder.class);
        final String session1 = "1";
        final String session2 = "2";

        final TopicPartition test0 = new TopicPartition(TOPIC, 0);
        final TopicPartition test1 = new TopicPartition(TOPIC, 1);
        final List<LogbrokerCookiesHolder> expectedCookies = new ArrayList<>();
        final List<TopicPartitionState<String>> expectedPartitionStates = new ArrayList<>();

        fetcher.registerTopicPartition(test0);
        fetcher.registerTopicPartition(test1);

        /* emit message 1 */

        fetcher.handleReadResponse(
                session1,
                new UnpackedReadResponse<>(
                        List.of(createUnpackedBatch(TOPIC, 0, 1, 10, 100)),
                        100
                ),
                readResponder
        );
        expectedCookies.add(new LogbrokerCookiesHolder(session1, List.of(100L), readResponder));
        expectedPartitionStates.add(new TopicPartitionState<>(test0, 10));
        expectedPartitionStates.add(new TopicPartitionState<>(test1, Long.MIN_VALUE));

        verify(sourceContext, times(1)).collectWithTimestamp("test_0", 100);
        assertEquals(expectedCookies, fetcher.getCookiesWithoutCheckpoint());
        assertEquals(
                Set.copyOf(expectedPartitionStates),
                Set.copyOf(fetcher.getPartitionStates())
        );

        /* emit message 2 */

        fetcher.handleReadResponse(
                session1,
                new UnpackedReadResponse<>(
                        List.of(createUnpackedBatch(TOPIC, 0, 2, 20, 200)),
                        101
                ),
                readResponder
        );
        expectedCookies.add(new LogbrokerCookiesHolder(session1, List.of(101L), readResponder));
        expectedPartitionStates.get(0).setOffset(21);

        verify(sourceContext, times(1)).collectWithTimestamp("test_0", 200);
        verify(sourceContext, times(1)).collectWithTimestamp("test_1", 201);
        assertEquals(expectedCookies, fetcher.getCookiesWithoutCheckpoint());
        assertEquals(
                Set.copyOf(expectedPartitionStates),
                Set.copyOf(fetcher.getPartitionStates())
        );
        /* emit message 3 */

        fetcher.handleReadResponse(
                session2,
                new UnpackedReadResponse<>(
                        List.of(createUnpackedBatch(TOPIC, 1, 1, 20, 200)),
                        102
                ),
                readResponder
        );
        expectedCookies.add(new LogbrokerCookiesHolder(session2, List.of(102L), readResponder));
        expectedPartitionStates.get(1).setOffset(20);

        verify(sourceContext, times(2)).collectWithTimestamp("test_0", 200);
        assertEquals(expectedCookies, fetcher.getCookiesWithoutCheckpoint());
        assertEquals(
                Set.copyOf(expectedPartitionStates),
                Set.copyOf(fetcher.getPartitionStates())
        );

        /* checkpoint */
        List<Tuple2<TopicPartition, Long>> currentState;
        synchronized (checkpointLock) {
            currentState = fetcher.snapshotCurrentState(1234);
        }
        assertEquals(List.of(Tuple2.of(test0, 21L), Tuple2.of(test1, 20L)), currentState);
        assertTrue(fetcher.getCookiesWithoutCheckpoint().isEmpty());
        assertEquals(
                Map.of(
                        1234L,
                        List.of(
                                new LogbrokerCookiesHolder(session1, List.of(100L, 101L), readResponder),
                                new LogbrokerCookiesHolder(session2, List.of(102L), readResponder)
                        )
                ),
                fetcher.getPendingCheckpointCookies()
        );
        assertEquals(0L, fetcher.getPendingCommitCookiesCounter().get());

        /* commit */
        fetcher.commitLogbrokerCookies(1234L);
        assertEquals(
                Collections.<Long, List<LogbrokerCookiesHolder>>emptyMap(),
                fetcher.getPendingCheckpointCookies()
        );
        assertEquals(3L, fetcher.getPendingCommitCookiesCounter().get());
        verify(readResponder, times(1)).commit(List.of(100L, 101L));
        verify(readResponder, times(1)).commit(List.of(102L));

        /* ack commit*/
        fetcher.committed(session1, List.of(100L, 101L));
        assertEquals(1, fetcher.getPendingCommitCookiesCounter().get());
        fetcher.committed(session2, List.of(102L));
        assertEquals(0, fetcher.getPendingCommitCookiesCounter().get());
    }

    @Test
    @Timeout(5)
    public void testProcessingUnknownPartition() throws Exception {
        Object checkpointLock = new Object();
        SourceFunction.SourceContext<String> sourceContext = mock(SourceFunction.SourceContext.class);
        doReturn(checkpointLock).when(sourceContext).getCheckpointLock();

        final DummyStreamFetcher<String> fetcher = DummyStreamFetcher.builder(String.class)
                .setSourceContext(sourceContext)
                .build();

        try {
            // fetcher ожидает только данные для партиции с индексом 0
            fetcher.handleReadResponse(
                    "2",
                    new UnpackedReadResponse<>(
                            List.of(createUnpackedBatch(TOPIC, 1, 1, 20, 200)),
                            102
                    ),
                    mock(BatchingStreamListener.ReadResponder.class)
            );

            fail("no exception");
        } catch (FlinkLogbrokerException e) {
            assertTrue(e.getMessage().contains("Unknown partition"));
        }
    }

    @Test
    public void testUnknownCheckpointIdOnCommit() throws Exception {
        Object checkpointLock = new Object();
        SourceFunction.SourceContext<String> sourceContext = mock(SourceFunction.SourceContext.class);
        doReturn(checkpointLock).when(sourceContext).getCheckpointLock();

        final DummyStreamFetcher<String> fetcher = DummyStreamFetcher.builder(String.class)
                .setSourceContext(sourceContext)
                .build();

        /* commit */
        assertEquals(0, fetcher.getPendingCommitCookiesCounter().get());
        fetcher.commitLogbrokerCookies(4321L);
        assertEquals(0, fetcher.getPendingCommitCookiesCounter().get());
    }

    @Test
    public void testCommitDisabled() throws Exception {
        Object checkpointLock = new Object();
        SourceFunction.SourceContext<String> sourceContext = mock(SourceFunction.SourceContext.class);
        doReturn(checkpointLock).when(sourceContext).getCheckpointLock();

        final DummyStreamFetcher<String> fetcher = DummyStreamFetcher.builder(String.class)
                .setSourceContext(sourceContext)
                .setCommitsDisabled(true)
                .build();

        final BatchingStreamListener.ReadResponder readResponder = mock(BatchingStreamListener.ReadResponder.class);
        final TopicPartition test0 = new TopicPartition(TOPIC, 0);
        final List<TopicPartitionState<String>> expectedPartitionStates = new ArrayList<>();

        fetcher.registerTopicPartition(new TopicPartition(TOPIC, 0));

        /* emit message */

        fetcher.handleReadResponse(
                "1",
                new UnpackedReadResponse<>(
                        List.of(createUnpackedBatch(TOPIC, 0, 1, 10, 100)),
                        100
                ),
                readResponder
        );
        expectedPartitionStates.add(new TopicPartitionState<>(test0, 10));

        verify(sourceContext, times(1)).collectWithTimestamp("test_0", 100);
        // проверяем, что не было добавлено cookies для коммита
        assertEquals(Collections.emptyList(), fetcher.getCookiesWithoutCheckpoint());
        assertEquals(expectedPartitionStates, fetcher.getPartitionStates());

        /* checkpoint */
        List<Tuple2<TopicPartition, Long>> currentState;
        synchronized (checkpointLock) {
            currentState = new ArrayList<>(fetcher.snapshotCurrentState(1234L));
        }
        assertEquals(List.of(Tuple2.of(test0, 10L)), currentState);
        assertTrue(fetcher.getCookiesWithoutCheckpoint().isEmpty());
        // не должно быть никаких cookies
        assertEquals(
                Collections.<Long, List<LogbrokerCookiesHolder>>emptyMap(),
                fetcher.getPendingCheckpointCookies()
        );
        assertEquals(0L, fetcher.getPendingCommitCookiesCounter().get());

        /* commit */
        fetcher.commitLogbrokerCookies(1234L);
        assertEquals(0, fetcher.getPendingCommitCookiesCounter().get());
    }
}
