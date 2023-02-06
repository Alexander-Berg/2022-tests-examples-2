package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class RoleParams extends AbstractFormParameters {
    @FormParameter("uid")
    private Long uid;

    public void setUid(Long uid) {
        this.uid = uid;
    }

    public Long getUid() {
        return uid;
    }

    public RoleParams withUid(Long uid) {
        setUid(uid);
        return this;
    }
}
