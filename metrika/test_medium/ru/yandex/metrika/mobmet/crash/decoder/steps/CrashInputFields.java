package ru.yandex.metrika.mobmet.crash.decoder.steps;

import ru.yandex.metrika.segments.apps.bundles.AppEventType;

public class CrashInputFields {

    private final long eventId;
    private final long applicationId;
    private final String operatingSystem;
    private AppEventType eventType;
    private String eventName;
    private final byte[] eventValue;

    public CrashInputFields(long eventId,
                            long applicationId,
                            String operatingSystem,
                            AppEventType eventType,
                            String eventName,
                            byte[] eventValue) {
        this.eventId = eventId;
        this.applicationId = applicationId;
        this.operatingSystem = operatingSystem;
        this.eventType = eventType;
        this.eventName = eventName;
        this.eventValue = eventValue;
    }

    public long getEventId() {
        return eventId;
    }

    public long getApplicationId() {
        return applicationId;
    }

    public String getOperatingSystem() {
        return operatingSystem;
    }

    public Integer getEventType() {
        return eventType.getNumber();
    }

    public String getEventName() {
        return eventName;
    }

    public byte[] getEventValue() {
        return eventValue;
    }

}
