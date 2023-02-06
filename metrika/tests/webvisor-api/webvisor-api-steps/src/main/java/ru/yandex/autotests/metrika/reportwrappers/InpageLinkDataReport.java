package ru.yandex.autotests.metrika.reportwrappers;

import java.util.List;

import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataLinkMapGETSchema;
import ru.yandex.metrika.api.error.ApiError;

/**
 * Created by sonick on 19.12.16.
 */
public class InpageLinkDataReport extends InpageCommonReport<MapsV1DataLinkMapGETSchema> {

    public InpageLinkDataReport(MapsV1DataLinkMapGETSchema rawReport) {
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
        return rawReport.getMaxSampleShare();
    }

    @Override
    public Boolean getSampleable() {
        return rawReport.getSampleable();
    }

    @Override
    public Double getSampleShare() {
        return rawReport.getSampleShare();
    }

    @Override
    public String getMessage() {
        return rawReport.getMessage();
    }
}
