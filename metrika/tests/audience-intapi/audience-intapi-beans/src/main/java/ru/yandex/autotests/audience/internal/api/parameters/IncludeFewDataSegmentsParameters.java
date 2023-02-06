package ru.yandex.autotests.audience.internal.api.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class IncludeFewDataSegmentsParameters extends AbstractFormParameters {
    @FormParameter("include_few_data_segments")
    private int includeFewDataSegments;

    public int getIncludeFewDataSegments() {
        return includeFewDataSegments;
    }

    public void setIncludeFewDataSegments(int includeFewDataSegments) {
        this.includeFewDataSegments = includeFewDataSegments;
    }

    public IncludeFewDataSegmentsParameters withIncludeFewDataSegments(boolean flag) {
        setIncludeFewDataSegments(flag ? 1 : 0);
        return this;
    }

    public static IncludeFewDataSegmentsParameters includeFewDataSegments(boolean includeFewDataSegments) {
        return new IncludeFewDataSegmentsParameters().withIncludeFewDataSegments(includeFewDataSegments);
    }
}
