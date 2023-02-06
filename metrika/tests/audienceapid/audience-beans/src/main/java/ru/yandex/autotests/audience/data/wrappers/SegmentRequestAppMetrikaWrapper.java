package ru.yandex.autotests.audience.data.wrappers;

import ru.yandex.metrika.audience.pubapi.SegmentRequestAppMetrika;

/**
 * Created by konkov on 28.03.2017.
 */
public class SegmentRequestAppMetrikaWrapper extends WrapperBase<SegmentRequestAppMetrika> {

    protected SegmentRequestAppMetrikaWrapper(SegmentRequestAppMetrika value) {
        super(value);
    }

    public static SegmentRequestAppMetrikaWrapper wrap(SegmentRequestAppMetrika value) {
        return new SegmentRequestAppMetrikaWrapper(value);
    }

    @Override
    public String toString() {
        return value == null ? "<null>"
                : value.getName();
    }
}
