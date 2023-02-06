package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class ProfileAttributesParameters extends CommonReportParameters {

    @FormParameter("include_deleted")
    private boolean includeDeleted;

    public boolean isIncludeDeleted() {
        return includeDeleted;
    }

    public ProfileAttributesParameters includeDeleted() {
        this.includeDeleted = true;
        return this;
    }
}
