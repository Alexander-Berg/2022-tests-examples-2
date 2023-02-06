package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class GrantsParameters extends AbstractFormParameters {

    @FormParameter("quota_ignore")
    private boolean quotaIgnore;

    public boolean isQuotaIgnore() {
        return quotaIgnore;
    }

    public void setQuotaIgnore(boolean quotaIgnore) {
        this.quotaIgnore = quotaIgnore;
    }

    public GrantsParameters quotaIgnore() {
        this.quotaIgnore = true;
        return this;
    }
}
