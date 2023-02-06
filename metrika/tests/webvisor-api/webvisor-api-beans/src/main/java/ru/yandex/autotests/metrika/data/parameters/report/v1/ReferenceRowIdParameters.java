package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

import java.util.List;

import static java.lang.String.join;

public class ReferenceRowIdParameters extends AbstractFormParameters {

    @FormParameter("reference_row_id")
    private String referenceRowId;

    public String getReferenceRowId() {
        return referenceRowId;
    }

    public void setReferenceRowId(String referenceRowId) {
        this.referenceRowId = referenceRowId;
    }

    public ReferenceRowIdParameters withReferenceRowId(final List<String> referenceRowId) {
        this.referenceRowId = join(",", referenceRowId);
        return this;
    }

    public static ReferenceRowIdParameters referenceRowId(List<String> referenceRowId) {
        return new ReferenceRowIdParameters().withReferenceRowId(referenceRowId);
    }

}
