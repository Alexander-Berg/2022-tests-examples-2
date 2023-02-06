package ru.yandex.autotests.audience.data.wrappers;


import ru.yandex.metrika.audience.pubapi.SegmentRequestGeoCircle;

/**
 * Created by konkov on 28.03.2017.
 */
public class SegmentRequestGeoCircleWrapper extends WrapperBase<SegmentRequestGeoCircle> {

    protected SegmentRequestGeoCircleWrapper(SegmentRequestGeoCircle value) {
        super(value);
    }

    public static SegmentRequestGeoCircleWrapper wrap(SegmentRequestGeoCircle value) {
        return new SegmentRequestGeoCircleWrapper(value);
    }

    @Override
    public String toString() {
        return value == null ? "<null>"
                : value.getName();
    }
}
