package ru.yandex.autotests.metrika.appmetrica.parameters.profile.events;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class ProfileSessionsEventsParameters extends ProfileSessionsParametersBase {

    @FormParameter("sessionIds")
    private String sessionIds;

    public String getSessionIds() {
        return sessionIds;
    }

    public ProfileSessionsEventsParameters withSessionIds(String sessionIds) {
        this.sessionIds = sessionIds;
        return this;
    }
}
