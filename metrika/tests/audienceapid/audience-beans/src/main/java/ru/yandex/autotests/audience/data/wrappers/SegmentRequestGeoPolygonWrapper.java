package ru.yandex.autotests.audience.data.wrappers;


import ru.yandex.metrika.audience.pubapi.SegmentRequestGeoPolygon;

public class SegmentRequestGeoPolygonWrapper extends WrapperBase<SegmentRequestGeoPolygon> {

    protected SegmentRequestGeoPolygonWrapper(SegmentRequestGeoPolygon value) {
        super(value);
    }

    public static SegmentRequestGeoPolygonWrapper wrap(SegmentRequestGeoPolygon value) {
        return new SegmentRequestGeoPolygonWrapper(value);
    }

    @Override
    public String toString() {
        return value == null ? "<null>"
                : value.getName();
    }
}
