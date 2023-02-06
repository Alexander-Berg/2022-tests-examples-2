package ru.yandex.autotests.metrika.appmetrica.parameters;

import static com.google.common.base.Preconditions.checkNotNull;

/**
 * Created by graev on 30/01/2017.
 */
public final class CAConversion {

    private final Type type;

    private final String label;

    public static CAConversion toEventLabel(String label) {
        return new CAConversion(Type.CLIENT_EVENT, checkNotNull(label));
    }

    public static CAConversion anyActivity() {
        return new CAConversion(Type.ANY_ACTIVITY, null);
    }

    public static CAConversion sessionStart() {
        return new CAConversion(Type.SESSION_START, null);
    }

    private CAConversion(Type type, String label) {
        this.type = type;
        this.label = label;
    }

    public String getApiName() {
        return type.getApiName();
    }

    public String getEventLabel() {
        return label;
    }

    @Override
    public String toString() {
        switch (type) {
            case ANY_ACTIVITY:
                return "(any activity)";
            case SESSION_START:
                return "(session start)";
            case CLIENT_EVENT:
                return label;
        }

        throw new IllegalArgumentException("Unknown conversion type: " + type);
    }

    private enum Type {
        ANY_ACTIVITY(null),
        SESSION_START("session_start"),
        CLIENT_EVENT("client_event");

        private final String apiName;

        Type(String apiName) {
            this.apiName = apiName;
        }

        public String getApiName() {
            return apiName;
        }
    }
}
