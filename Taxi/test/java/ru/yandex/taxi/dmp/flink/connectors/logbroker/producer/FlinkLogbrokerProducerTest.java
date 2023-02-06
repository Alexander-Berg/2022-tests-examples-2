package ru.yandex.taxi.dmp.flink.connectors.logbroker.producer;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.core.testutils.CheckedThread;
import org.apache.flink.streaming.api.operators.StreamSink;
import org.apache.flink.streaming.runtime.streamrecord.StreamRecord;
import org.apache.flink.streaming.util.OneInputStreamOperatorTestHarness;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import ru.yandex.kikimr.persqueue.producer.AsyncProducer;
import ru.yandex.kikimr.persqueue.producer.async.AsyncProducerConfig;
import ru.yandex.kikimr.persqueue.producer.transport.message.inbound.ProducerInitResponse;
import ru.yandex.kikimr.persqueue.producer.transport.message.inbound.ProducerWriteResponse;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.TestInstallations;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.ThreadTestUtils;

import static java.lang.Thread.State.TIMED_WAITING;
import static java.lang.Thread.State.WAITING;
import static org.junit.Assert.fail;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;


class FlinkLogbrokerProducerTest {
    public static final String TOPIC = "dummy";

    @Test
    public void testAsyncErrorRethrownOnInvoke() throws Throwable {
        assertAsyncErrorRethrownOnCheckpoint(
                testHarness -> testHarness.processElement(new StreamRecord<>("msg-2")),
                exception -> {
                    assertTrue(exception.getMessage().contains("An error occurred while writing data to Logbroker"));
                    assertTrue(exception.getCause().getMessage().contains("ack exception"));
                }
        );
    }

    @Test
    public void testAsyncErrorRethrownOnCheckpoint() throws Throwable {
        assertAsyncErrorRethrownOnCheckpoint(
                testHarness -> testHarness.snapshot(123L, 123L),
                exception -> {
                    assertTrue(exception.getCause().getMessage().contains("An error occurred while writing data to " +
                            "Logbroker"));
                    assertTrue(exception.getCause().getCause().getMessage().contains("ack exception"));
                }
        );
    }

    private interface HarnessConsumer {
        void accept(OneInputStreamOperatorTestHarness<String, Object> harness) throws Exception;
    }

    private void assertAsyncErrorRethrownOnCheckpoint(HarnessConsumer consumer,
                                                      Consumer<Exception> assertException) throws Throwable {
        final MockFlinkLogbrokerProducer producer = new MockFlinkLogbrokerProducer();

        OneInputStreamOperatorTestHarness<String, Object> testHarness =
                new OneInputStreamOperatorTestHarness<>(new StreamSink<>(producer));
        testHarness.open();

        testHarness.processElement(new StreamRecord<>("msg-1"));

        // let the message request return an async exception
        producer.acks.get(0).completeExceptionally(new Exception("ack exception"));

        try {
            consumer.accept(testHarness);
        } catch (Exception e) {
            // the next invoke should rethrow the async exception
            assertException.accept(e);
            // test succeeded
            return;
        }

        fail();
    }

    @Test
    @Timeout(2)
    public void testPendingTimeout() throws Throwable {
        LogbrokerProducerConfig config = LogbrokerProducerConfig
                .builder(TOPIC)
                .setPendingTimeout(100, TimeUnit.MILLISECONDS)
                .build();

        final MockFlinkLogbrokerProducer producer = new MockFlinkLogbrokerProducer(config);

        OneInputStreamOperatorTestHarness<String, Object> testHarness =
                new OneInputStreamOperatorTestHarness<>(new StreamSink<>(producer));
        testHarness.open();

        testHarness.processElement(new StreamRecord<>("msg-1"));

        try {
            testHarness.snapshot(123L, 123L);
        } catch (Exception e) {
            assertTrue(e.getCause().getMessage().contains("An error occurred while writing data to Logbroker"));
            assertEquals(
                    e.getCause().getCause().getClass(),
                    java.util.concurrent.TimeoutException.class
            );
            return;
        }

        fail();
    }

    @Test
    @Timeout(2)
    public void testPendingAcks() throws Throwable {
        final MockFlinkLogbrokerProducer producer = new MockFlinkLogbrokerProducer();

        OneInputStreamOperatorTestHarness<String, Object> testHarness =
                new OneInputStreamOperatorTestHarness<>(new StreamSink<>(producer));
        testHarness.open();

        testHarness.processElement(new StreamRecord<>("msg-1"));
        testHarness.processElement(new StreamRecord<>("msg-2"));
        testHarness.processElement(new StreamRecord<>("msg-3"));

        verify(producer.mockProducer, times(3)).write(
                any(byte[].class), any(Long.class), any(Long.class)
        );

        assertEquals(producer.pendingAcksCount(), 3);

        producer.acks.get(0).complete(new ProducerWriteResponse(1, 1, false));
        assertEquals(producer.pendingAcksCount(), 2);

        CheckedThread snapshotThread = new CheckedThread() {
            @Override
            public void go() throws Exception {
                // this should block until all records are flushed;
                testHarness.snapshot(123L, 123L);
            }
        };
        snapshotThread.start();
        ThreadTestUtils.waitNonTerminatedState(snapshotThread, Set.of(TIMED_WAITING, WAITING));

        producer.acks.get(1).complete(new ProducerWriteResponse(2, 2, false));
        producer.acks.get(2).complete(new ProducerWriteResponse(3, 3, false));

        snapshotThread.sync();
        assertEquals(producer.pendingAcksCount(), 0);
    }

    private static class MockFlinkLogbrokerProducer extends FlinkLogbrokerProducer<String> {
        public transient AsyncProducer mockProducer;
        public transient List<CompletableFuture<ProducerWriteResponse>> acks;

        private MockFlinkLogbrokerProducer() {
            this(LogbrokerProducerConfig.getDefaultConfig(TOPIC));
        }

        private MockFlinkLogbrokerProducer(LogbrokerProducerConfig config) {
            super(TestInstallations.TEST, config, new SimpleStringSchema());
            this.mockProducer = mock(AsyncProducer.class);
            this.acks = new ArrayList<>();

            when(
                    mockProducer.write(any(byte[].class), any(Long.class), any(Long.class))
            ).thenAnswer(invocation -> {
                CompletableFuture<ProducerWriteResponse> future = new CompletableFuture<>();
                acks.add(future);
                return future;
            });
        }


        @Override
        protected ProducerInitResponse initProducer(AsyncProducerConfig config) throws InterruptedException,
                ExecutionException {
            this.producer = mockProducer;
            return new ProducerInitResponse(1, TOPIC, 0, "dummy1");
        }
    }
}
