package ru.yandex.autotests.metrika.data.parameters.webvisor.v2;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;

/**
 * Created by sourx on 24.04.17.
 */
public class VisitViewedParameters extends VisitsGridParameters {
    @FormParameter("visit_id")
    private String visitId;

    public String getVisitId() {
        return visitId;
    }

    public void setVisitId(String visitId) {
        this.visitId = visitId;
    }

    public VisitViewedParameters withVisitId(String visitId) {
        this.visitId = visitId;
        return this;
    }
}
