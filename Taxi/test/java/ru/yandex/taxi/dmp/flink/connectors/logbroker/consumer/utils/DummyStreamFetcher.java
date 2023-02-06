package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils;


import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicLong;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.metrics.MetricGroup;
import org.apache.flink.metrics.groups.UnregisteredMetricsGroup;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.streaming.runtime.tasks.ProcessingTimeService;
import org.apache.flink.streaming.runtime.tasks.TestProcessingTimeService;
import org.apache.flink.streaming.util.MockDeserializationSchema;
import org.apache.flink.util.SerializedValue;

import ru.yandex.kikimr.persqueue.consumer.BatchingStreamListener;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerReadResponse;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.ThreadTestUtils;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.BaseStreamFetcher;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.LogbrokerCookiesHolder;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.PartitionAssigner;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.Supervisor;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.TopicPartition;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.internal.TopicPartitionState;

import static org.mockito.Mockito.mock;

public class DummyStreamFetcher<T> extends BaseStreamFetcher<T> implements ThreadTestUtils.BlockedClosable {

    @SuppressWarnings("ParameterNumber")
    public DummyStreamFetcher(SourceFunction.SourceContext<T> sourceContext,
                              Map<TopicPartition, Long> seedPartitionsWithInitialOffsets,
                              SerializedValue<WatermarkStrategy<T>> watermarkStrategy,
                              ProcessingTimeService processingTimeProvider,
                              long autoWatermarkInterval,
                              DeserializationSchema<T> deserializer,
                              PartitionAssigner partitionAssigner,
                              CompletableFuture<?> observedNewPartitionsFuture,
                              boolean commitsDisabled,
                              MetricGroup consumerMetricGroup) throws Exception {
        super(
                sourceContext,
                seedPartitionsWithInitialOffsets,
                watermarkStrategy,
                processingTimeProvider,
                autoWatermarkInterval,
                DummyStreamFetcher.class.getClassLoader(),
                deserializer,
                partitionAssigner,
                observedNewPartitionsFuture,
                commitsDisabled,
                consumerMetricGroup
        );
    }

    public Supervisor getSupervisor() {
        return supervisor;
    }

    public List<TopicPartitionState<T>> getPartitionStates() {
        return List.copyOf(partitionStates.values());
    }

    public List<LogbrokerCookiesHolder> getCookiesWithoutCheckpoint() {
        return cookiesWithoutCheckpoint;
    }

    public Map<Long, List<LogbrokerCookiesHolder>> getPendingCheckpointCookies() {
        return pendingCheckpointCookies;
    }

    public AtomicLong getPendingCommitCookiesCounter() {
        return pendingCommitCookiesCounter;
    }

    @Override
    public Supervisor startConsume(Set<Integer> partitions) throws Exception {
        return mock(Supervisor.class);
    }

    @Override
    protected void readRawMessage(String sessionId,
                          ConsumerReadResponse read,
                          BatchingStreamListener.ReadResponder readResponder) throws Exception {

    }

    @Override
    public void close() throws Exception {
        cancel();
    }

    @Override
    public void blockByTest(Callable<Void> callable) throws Exception {
        synchronized (this) {
            callable.call();
        }
    }

    @Override
    public Thread.State getBlockedThreadState() {
        return Thread.State.BLOCKED;
    }

    public static <T> Builder<T> builder() {
        return new Builder<>();
    }

    public static <T> Builder<T> builder(Class<T> tClass) {
        return new Builder<>(tClass);
    }

    public static class Builder<T> {
        private SourceFunction.SourceContext<T> sourceContext = mock(SourceFunction.SourceContext.class);
        private Map<TopicPartition, Long> seedPartitionsWithInitialOffsets = Collections.emptyMap();
        private SerializedValue<WatermarkStrategy<T>> watermarkStrategy = null;
        private ProcessingTimeService processingTimeProvider = new TestProcessingTimeService();
        private long autoWatermarkInterval = 0;
        private DeserializationSchema<T> deserializer = new MockDeserializationSchema<>();
        private PartitionAssigner partitionAssigner = new PartitionAssigner(0, 1, 1);
        private CompletableFuture<?> observedNewPartitionsFuture = new CompletableFuture<>();
        private boolean commitsDisabled = false;

        public Builder() {
        }

        public Builder(Class<T> tClass) {
            deserializer = new TypedMockDeserializationSchema<>(tClass);
        }

        public Builder<T> setSourceContext(SourceFunction.SourceContext<T> sourceContext) {
            this.sourceContext = sourceContext;
            return this;
        }

        public Builder<T> setSeedPartitionsWithInitialOffsets(
                Map<TopicPartition, Long> seedPartitionsWithInitialOffsets) {
            this.seedPartitionsWithInitialOffsets = seedPartitionsWithInitialOffsets;
            return this;
        }

        public Builder<T> setWatermarkStrategy(SerializedValue<WatermarkStrategy<T>> watermarkStrategy) {
            this.watermarkStrategy = watermarkStrategy;
            return this;
        }

        public Builder<T> setProcessingTimeProvider(ProcessingTimeService processingTimeProvider) {
            this.processingTimeProvider = processingTimeProvider;
            return this;
        }

        public Builder<T> setAutoWatermarkInterval(long autoWatermarkInterval) {
            this.autoWatermarkInterval = autoWatermarkInterval;
            return this;
        }

        public Builder<T> setDeserializer(DeserializationSchema<T> deserializer) {
            this.deserializer = deserializer;
            return this;
        }


        public Builder<T> setPartitionAssigner(PartitionAssigner partitionAssigner) {
            this.partitionAssigner = partitionAssigner;
            return this;
        }

        public Builder<T> setObservedNewPartitionsFuture(CompletableFuture<?> observedNewPartitionsFuture) {
            this.observedNewPartitionsFuture = observedNewPartitionsFuture;
            return this;
        }

        public Builder<T> setCommitsDisabled(boolean commitsDisabled) {
            this.commitsDisabled = commitsDisabled;
            return this;
        }

        public DummyStreamFetcher<T> build() throws Exception {
            return new DummyStreamFetcher<>(
                    sourceContext,
                    seedPartitionsWithInitialOffsets,
                    watermarkStrategy,
                    processingTimeProvider,
                    autoWatermarkInterval,
                    deserializer,
                    partitionAssigner,
                    observedNewPartitionsFuture,
                    commitsDisabled,
                    new UnregisteredMetricsGroup()
            );
        }
    }
}
