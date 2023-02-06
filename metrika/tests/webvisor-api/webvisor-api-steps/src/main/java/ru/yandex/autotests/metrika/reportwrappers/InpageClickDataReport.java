package ru.yandex.autotests.metrika.reportwrappers;

import java.util.List;

import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataClickGETSchema;
import ru.yandex.metrika.api.error.ApiError;

/**
 * Created by sonick on 19.12.16.
 */
public class InpageClickDataReport extends InpageCommonReport<MapsV1DataClickGETSchema> {

    public InpageClickDataReport(MapsV1DataClickGETSchema rawReport) {
        super(rawReport);
    }

    @Override
    public Long getCode() {
        return rawReport.getCode();
    }

    @Override
    public List<ApiError> getErrors() {
        return rawReport.getErrors();
    }

    @Override
    public Double getMaxSampleShare() {
        return rawReport.getData().getMaxSampleShare();
    }

    @Override
    public Boolean getSampleable() {
        return rawReport.getData().getSampleable();
    }

    @Override
    public Double getSampleShare() {
        return rawReport.getData().getSampleShare();
    }

    @Override
    public String getMessage() {
        return rawReport.getMessage();
    }
}
