package ru.yandex.autotests.metrika.appmetrica.parameters.profile.events;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.metrika.segments.apps.bundles.AppEventSource;

public class ProfileEventParameters extends ProfileSessionsParametersBase {

    @FormParameter("sessionId")
    private String sessionId;

    @FormParameter("eventNumber")
    private String eventNumber;

    @FormParameter("eventDateTime")
    private String eventDateTime;

    @FormParameter("eventSource")
    private AppEventSource eventSource;

    public String getSessionId() {
        return sessionId;
    }

    public ProfileEventParameters withSessionId(String sessionId) {
        this.sessionId = sessionId;
        return this;
    }

    public String getEventNumber() {
        return eventNumber;
    }

    public ProfileEventParameters withEventNumber(String eventNumber) {
        this.eventNumber = eventNumber;
        return this;
    }

    public String getEventDateTime() {
        return eventDateTime;
    }

    public ProfileEventParameters withEventDateTime(String eventDateTime) {
        this.eventDateTime = eventDateTime;
        return this;
    }

    public AppEventSource getEventSource() {
        return eventSource;
    }

    public ProfileEventParameters withEventSource(AppEventSource eventSource) {
        this.eventSource = eventSource;
        return this;
    }
}
