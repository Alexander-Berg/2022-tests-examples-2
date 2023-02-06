package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils;

import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.runtime.streamrecord.StreamRecord;

/**
 * копи-паст org.apache.flink.streaming.connectors.kafka.testutils.TestSourceContext
 */
public class TestSourceContext<T> implements SourceFunction.SourceContext<T> {

    private final Object checkpointLock = new Object();
    private final Object watermarkLock = new Object();

    private volatile StreamRecord<T> latestElement;
    private volatile Watermark currentWatermark;

    @Override
    public void collect(T element) {
        this.latestElement = new StreamRecord<>(element);
    }

    @Override
    public void collectWithTimestamp(T element, long timestamp) {
        this.latestElement = new StreamRecord<>(element, timestamp);
    }

    @Override
    public void emitWatermark(Watermark mark) {
        synchronized (watermarkLock) {
            currentWatermark = mark;
            watermarkLock.notifyAll();
        }
    }

    @Override
    public void markAsTemporarilyIdle() {
        // do nothing
    }

    @Override
    public Object getCheckpointLock() {
        return checkpointLock;
    }

    @Override
    public void close() {
        // do nothing
    }

    public StreamRecord<T> getLatestElement() {
        return latestElement;
    }

    public boolean hasWatermark() {
        return currentWatermark != null;
    }

    public Watermark getLatestWatermark() throws InterruptedException {
        synchronized (watermarkLock) {
            while (currentWatermark == null) {
                watermarkLock.wait();
            }
            Watermark wm = currentWatermark;
            currentWatermark = null;
            return wm;
        }
    }
}
