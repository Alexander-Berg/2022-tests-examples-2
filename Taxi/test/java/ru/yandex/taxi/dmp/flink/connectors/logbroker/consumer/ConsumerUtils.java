package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import NLogBroker.Common;
import NLogBroker.ConfigManager;
import com.google.common.primitives.Longs;
import org.apache.flink.api.common.state.ListState;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.util.MockStreamingRuntimeContext;
import org.mockito.ArgumentCaptor;

import ru.yandex.kikimr.persqueue.compression.CompressionCodec;
import ru.yandex.kikimr.persqueue.consumer.BatchingStreamConsumer;
import ru.yandex.kikimr.persqueue.consumer.BatchingStreamListener;
import ru.yandex.kikimr.persqueue.consumer.stream.BasicStreamListener;
import ru.yandex.kikimr.persqueue.consumer.transport.message.CommitMessage;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerInitResponse;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerLockMessage;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerReadResponse;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageBatch;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageData;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageMeta;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.InternalStreamListener;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.MockFunctionInitializationContext;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils.MockOperatorStateStore;

import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

public class ConsumerUtils {

    private ConsumerUtils() { }

    static class ConsumerHelper {
        final String topicId;
        InternalStreamListener<Long> listener;
        final int partitionCount;
        final BatchingStreamConsumer mockConsumer = mock(BatchingStreamConsumer.class);
        final BatchingStreamListener.ReadResponder mockReadResponder = mock(BatchingStreamListener.ReadResponder.class);

        ConsumerHelper(String topicId, int partitionCount) {
            this.topicId = topicId;
            this.partitionCount = partitionCount;
        }

        void init() {
            ArgumentCaptor<InternalStreamListener<Long>> listenerCaptor =
                    ArgumentCaptor.forClass(InternalStreamListener.class);
            verify(mockConsumer, times(1)).startConsume(listenerCaptor.capture());
            listener = listenerCaptor.getValue();

            listener.onInit(new ConsumerInitResponse("session_" + topicId));
            IntStream.range(0, partitionCount).forEach(i ->
                    listener.onLock(
                            new ConsumerLockMessage(topicId, i, 0, 1000, 1000),
                            mock(BasicStreamListener.LockResponder.class)
                    )
            );

            doAnswer(inv -> {
                listener.onClose();
                return null;
            }).when(mockConsumer).stopConsume();

        }

        void emitRecords(List<Tuple2<Long, Long>> records, int partition, long cookies) {
            final List<MessageData> messages = records.stream().map(tp ->
                    new MessageData(
                            Longs.toByteArray(tp.f0),
                            tp.f1,
                            new MessageMeta(
                                    new byte[]{}, 0, tp.f0, tp.f0 + 1, "", CompressionCodec.RAW,
                                    Collections.emptyMap()
                            )
                    )
            ).collect(Collectors.toList());

            MessageBatch batch = new MessageBatch(topicId, partition, new ArrayList<>(messages));
            final ConsumerReadResponse consumerReadResponse = new ConsumerReadResponse(
                    new ArrayList<>(Arrays.asList(batch)),
                    cookies
            );

            listener.onRead(consumerReadResponse, mockReadResponder);
        }

        void commited(List<Long> cookies) {
            listener.onCommit(new CommitMessage(cookies));
        }
    }

    public static <T> void setupConsumer(BaseLogbrokerConsumer<T> consumer) throws Exception {
        setupConsumer(
                consumer,
                false,
                null,
                true,
                0,
                1
        );
    }

    public static <T, S> void setupConsumer(
            BaseLogbrokerConsumer<T> consumer,
            boolean isRestored,
            ListState<S> restoredListState,
            boolean isCheckpointingEnabled,
            int subtaskIndex,
            int totalNumSubtasks) throws Exception {

        // run setup procedure in operator life cycle
        initConsumer(consumer, isRestored, restoredListState, isCheckpointingEnabled, subtaskIndex, totalNumSubtasks);
        consumer.open(new Configuration());
    }

    public static <T> void initConsumer(BaseLogbrokerConsumer<T> consumer) throws Exception {
        initConsumer(
                consumer,
                false,
                null,
                true,
                0,
                1
        );
    }

    public static <T, S> void initConsumer(
            BaseLogbrokerConsumer<T> consumer,
            boolean isRestored,
            ListState<S> restoredListState,
            boolean isCheckpointingEnabled,
            int subtaskIndex,
            int totalNumSubtasks) throws Exception {

        // run setup procedure in operator life cycle
        consumer.setRuntimeContext(new MockStreamingRuntimeContext(isCheckpointingEnabled, totalNumSubtasks,
                subtaskIndex));
        consumer.initializeState(new MockFunctionInitializationContext(isRestored,
                new MockOperatorStateStore(restoredListState)));
    }

    public static ConfigManager.DescribeTopicResult buildTopicResult(int partitionCount) {
        final Common.IntOrDefaultValue partitionCountValue =
                Common.IntOrDefaultValue.newBuilder()
                        .setUserDefined(partitionCount)
                        .build();

        return ConfigManager.DescribeTopicResult.newBuilder()
                .setProperties(
                        Common.TopicProperties.newBuilder()
                                .setPartitionsCount(partitionCountValue)
                                .build())
                .build();
    }
}
