package ru.yandex.autotests.audience.data.wrappers;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import ru.yandex.metrika.audience.pubapi.SegmentRequestDmp;

/**
 * Created by ava1on on 05.07.17.
 */
public class SegmentRequestDmpWrapper extends WrapperBase<SegmentRequestDmp> {
    protected SegmentRequestDmpWrapper(SegmentRequestDmp value) {
        super(value);
    }

    public static SegmentRequestDmpWrapper wrap(SegmentRequestDmp value) {
        return new SegmentRequestDmpWrapper(value);
    }

    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this.get(), ToStringStyle.JSON_STYLE);
    }
}
