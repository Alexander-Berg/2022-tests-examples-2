package ru.yandex.autotests.audience.data.wrappers;

import ru.yandex.metrika.audience.pubapi.SegmentRequestMetrika;

/**
 * Created by konkov on 28.03.2017.
 */
public class SegmentRequestMetrikaWrapper extends WrapperBase<SegmentRequestMetrika> {

    protected SegmentRequestMetrikaWrapper(SegmentRequestMetrika value) {
        super(value);
    }

    public static SegmentRequestMetrikaWrapper wrap(SegmentRequestMetrika value) {
        return new SegmentRequestMetrikaWrapper(value);
    }

    @Override
    public String toString() {
        return value == null ? "<null>"
                : value.getName();
    }
}
