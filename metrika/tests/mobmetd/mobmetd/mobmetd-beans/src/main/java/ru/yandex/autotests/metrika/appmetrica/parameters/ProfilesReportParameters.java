package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class ProfilesReportParameters extends TableReportParameters {

    @FormParameter("intervals_length")
    private Double intervalsLength = 0.0;

    public Double getIntervalsLength() {
        return intervalsLength;
    }

    public ProfilesReportParameters withIntervalsLength(Double intervalsLength) {
        this.intervalsLength = intervalsLength;
        return this;
    }

}
