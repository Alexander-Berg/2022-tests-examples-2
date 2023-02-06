package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal;

import java.util.Collections;
import java.util.Map;
import java.util.stream.Stream;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import ru.yandex.kikimr.persqueue.consumer.stream.BasicStreamListener.LockResponder;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerLockMessage;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.FlinkLogbrokerException;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.DummyStreamFetcher;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.fail;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

class InternalStreamListenerTest {
    public static final String TOPIC = "dummyTopic";

    private static Stream<Arguments> lockSource() {
        return Stream.of(
                Arguments.of(
                        119L,
                        lockMessage(0, 120L),
                        120L),
                Arguments.of(
                        220L,
                        lockMessage(0, 120L),
                        221L),
                Arguments.of(
                        Long.MIN_VALUE,
                        lockMessage(0, 120L),
                        120L)
        );
    }

    @ParameterizedTest
    @MethodSource("lockSource")
    public void testOnLock(long state,
                           ConsumerLockMessage lock,
                           long expectedReadOffset) {
        BaseStreamFetcher<?> fetcher = mock(BaseStreamFetcher.class);
        StreamSupervisor supervisor = mock(StreamSupervisor.class);
        InternalStreamListener<?> listener = new InternalStreamListener<>(fetcher, supervisor);
        doReturn(state).when(fetcher).registerTopicPartition(any());

        LockResponder lockResponse = mock(LockResponder.class);
        listener.onLock(lock, lockResponse);
        verify(lockResponse, times(1)).locked(expectedReadOffset, false);
    }

    private static Stream<Arguments> lockNonAssignedPartitionSource() {
        return Stream.of(
                // пришла партиция о существовании которой нам не было известно
                Arguments.of(
                        new PartitionAssigner(0, 1, 1),
                        lockMessage(1, 120L)),
                // партиция не назначена тек. таску/воркеру
                Arguments.of(
                        new PartitionAssigner(0, 2, 4),
                        lockMessage(1, 120L))
        );
    }

    @ParameterizedTest
    @MethodSource("lockNonAssignedPartitionSource")
    public void testOnLockThrowNonAssignedPartition(PartitionAssigner partitionAssigner,
                                                    ConsumerLockMessage lock) throws Exception {
        DummyStreamFetcher<String> fetcher =
                DummyStreamFetcher.builder(String.class)
                        .setPartitionAssigner(partitionAssigner)
                        .build();

        StreamSupervisor supervisor = mock(StreamSupervisor.class);
        InternalStreamListener<?> listener = new InternalStreamListener<>(fetcher, supervisor);

        LockResponder lockResponse = mock(LockResponder.class);
        try {
            listener.onLock(lock, lockResponse);
            fail("no exception");
        } catch (FlinkLogbrokerException e) {
            TopicPartition topicPartition = new TopicPartition(lock.getTopic(), lock.getPartition());
            assertEquals("Unknown partition: " + topicPartition, e.getCause().getMessage());
        }
    }

    /*-----------------------------------------------------------------------------*/

    private static ConsumerLockMessage lockMessage(int partition, long readOffset) {
        return new ConsumerLockMessage(
                TOPIC, partition, readOffset, readOffset, 0
        );
    }

    private static Map<TopicPartition, Long> state(int partition, Long stateOffset) {
        return Collections.singletonMap(new TopicPartition(TOPIC, partition), stateOffset);
    }

}
