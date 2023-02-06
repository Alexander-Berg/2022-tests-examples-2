package ru.yandex.autotests.audience.data.wrappers;

import ru.yandex.metrika.audience.pubapi.SegmentRequestPixel;

/**
 * Created by konkov on 31.03.2017.
 */
public class SegmentRequestPixelWrapper extends WrapperBase<SegmentRequestPixel> {
    protected SegmentRequestPixelWrapper(SegmentRequestPixel value) {
        super(value);
    }

    public static SegmentRequestPixelWrapper wrap(SegmentRequestPixel value) {
        return new SegmentRequestPixelWrapper(value);
    }

    @Override
    public String toString() {
        return value == null ? "<null>"
                : value.getName();
    }
}
