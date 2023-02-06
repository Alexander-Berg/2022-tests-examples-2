package ru.yandex.metrika.zkqueue.framework.listener.aggregate;

import java.util.stream.Collectors;

/**
 * Simple combiner which concatenates items
 */
final class ConcatCombiner extends SingletonCombiner {
    @Override
    public String singletonCombine(CombiningState state) {
        return state.consumedItems().stream()
                .map(ConsumedItem::payload)
                .collect(Collectors.joining());
    }
}
