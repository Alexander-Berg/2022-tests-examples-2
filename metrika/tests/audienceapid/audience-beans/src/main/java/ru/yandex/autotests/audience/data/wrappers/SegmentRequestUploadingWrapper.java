package ru.yandex.autotests.audience.data.wrappers;

import ru.yandex.metrika.audience.pubapi.SegmentRequestUploading;

/**
 * Created by konkov on 28.03.2017.
 */
public class SegmentRequestUploadingWrapper extends WrapperBase<SegmentRequestUploading> {

    protected SegmentRequestUploadingWrapper(SegmentRequestUploading value) {
        super(value);
    }

    public static SegmentRequestUploadingWrapper wrap(SegmentRequestUploading value) {
        return new SegmentRequestUploadingWrapper(value);
    }

    @Override
    public String toString() {
        return value == null ? "<null>"
                : value.getName();
    }
}
