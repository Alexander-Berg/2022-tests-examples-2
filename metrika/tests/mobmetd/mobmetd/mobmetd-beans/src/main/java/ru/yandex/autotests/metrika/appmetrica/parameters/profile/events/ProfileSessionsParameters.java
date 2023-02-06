package ru.yandex.autotests.metrika.appmetrica.parameters.profile.events;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;

public class ProfileSessionsParameters extends ProfileSessionsParametersBase {

    @FormParameter("eventName")
    private String eventName;

    @FormParameter("eventType")
    private AppEventType eventType;

    @FormParameter("includeBackground")
    private Boolean includeBackground;

    public String getEventName() {
        return eventName;
    }

    public ProfileSessionsParameters withEventName(String eventName) {
        this.eventName = eventName;
        return this;
    }

    public AppEventType getEventType() {
        return eventType;
    }

    public ProfileSessionsParameters withEventType(AppEventType eventType) {
        this.eventType = eventType;
        return this;
    }

    public Boolean getIncludeBackground() {
        return includeBackground;
    }

    public ProfileSessionsParameters withIncludeBackground(Boolean includeBackground) {
        this.includeBackground = includeBackground;
        return this;
    }
}
