package ru.yandex.autotests.audience.internal.api.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * Created by apuzikov on 17.07.17.
 */
public class GetUsersParameters extends AbstractFormParameters {

    private Long days;
    private Long uid;

    @FormParameter("condition")
    private String condition;

    public String getCondition() {
        condition = String.format("id==%d interval %d days", uid, days);
        return condition;
    }

    public GetUsersParameters withDays(long days) {
        this.days = days;
        return this;
    }

    public GetUsersParameters withUid(long uid) {
        this.uid = uid;
        return this;
    }

    public long getDays() {
        return days;
    }

    public void setDays(long days) {
        this.days = days;
    }

    public long getUid() {
        return uid;
    }

    public void setUid(long uid) {
        this.uid = uid;
    }
}