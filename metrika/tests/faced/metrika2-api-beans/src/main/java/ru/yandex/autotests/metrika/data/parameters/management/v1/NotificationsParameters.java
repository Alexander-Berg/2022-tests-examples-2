package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class NotificationsParameters extends AbstractFormParameters {

    @FormParameter("lang")
    private String lang;

    @FormParameter("obj_id")
    private Long objId;

    public String getLang() {
        return lang;
    }

    public void setLang(String lang) {
        this.lang = lang;
    }

    public Long getObjId() {
        return objId;
    }

    public void setObjId(Long objId) {
        this.objId = objId;
    }

    public NotificationsParameters withLang(String lang) {
        this.lang = lang;
        return this;
    }

    public NotificationsParameters withObjId(Long objId) {
        this.objId = objId;
        return this;
    }
}
