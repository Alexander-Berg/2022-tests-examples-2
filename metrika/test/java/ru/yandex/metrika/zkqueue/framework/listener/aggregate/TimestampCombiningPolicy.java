package ru.yandex.metrika.zkqueue.framework.listener.aggregate;

import static java.lang.System.currentTimeMillis;

/**
 * Flush messages when {@code timeThresholdMs} milliseconds were passed from aggregation start
 */
final class TimestampCombiningPolicy implements CombiningPolicy {

    private final long timeThresholdMs;

    TimestampCombiningPolicy(long timeThresholdMs) {
        this.timeThresholdMs = timeThresholdMs;
    }

    @Override
    public boolean shouldFlush(CombiningState state) {
        return currentTimeMillis() - state.aggregationStartTimestamp() > timeThresholdMs;
    }
}
