package ru.yandex.autotests.audience.internal.api.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;

/**
 * Created by apuzikov on 17.07.17.
 */
public class UidParameters extends AbstractFormParameters {
    @FormParameter("uid")
    private String uid;

    public String getUid() {
        return uid;
    }

    public void setUid(long... uid) {
        this.uid = JsonUtils.toString(uid, true);
    }

    public UidParameters() {
        this.uid = uid;
    }

    public UidParameters withUid(long... uid) {
        setUid(uid);
        return this;
    }

    public static UidParameters uid(long... uid) {
        return new UidParameters().withUid(uid);
    }
}
