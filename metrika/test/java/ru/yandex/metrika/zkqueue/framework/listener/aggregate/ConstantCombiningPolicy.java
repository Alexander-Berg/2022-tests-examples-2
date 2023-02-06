package ru.yandex.metrika.zkqueue.framework.listener.aggregate;

/**
 * Flush messages after fixed amount
 */
final class ConstantCombiningPolicy implements CombiningPolicy {

    private final int thresholdCount;

    ConstantCombiningPolicy(int thresholdCount) {
        this.thresholdCount = thresholdCount;
    }

    @Override
    public boolean shouldFlush(CombiningState state) {
        return state.consumedItems().size() >= thresholdCount;
    }
}
