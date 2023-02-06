package ru.yandex.autotests.audience.internal.api.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * Created by apuzikov on 29.07.17.
 */
public class CryptaParameters extends AbstractFormParameters {

    @FormParameter("segment_id")
    private long segmentId;

    public CryptaParameters withSegmentUid(long segmentUid) {
        this.segmentId = segmentUid;
        return this;
    }

    public static CryptaParameters segmentUid(long segmentUid) {
        return new CryptaParameters().withSegmentUid(segmentUid);
    }

    public void setSegmentId(long segmentId) {
        this.segmentId = segmentId;
    }

    public long getSegmentId() {
        return segmentId;
    }

}
