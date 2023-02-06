package ru.yandex.metrika.mobmet.crash.decoder.steps;

import ru.yandex.metrika.segments.apps.bundles.AppEventType;

public record CrashDataParams(
        long eventId,
        int appId,
        String os,
        AppEventType eventType,
        String eventName,
        String crashFieldsPath,
        String libraryCrashFieldsPath
) {

    public static CrashDataParams commonCrashParams(long eventId, int appId, String os, AppEventType eventType,
                                                    String crashFieldsPath) {
        return new CrashDataParams(eventId, appId, os, eventType, null, crashFieldsPath, null);
    }

    public static CrashDataParams iosErrorParams(long eventId, int appId, String os, AppEventType eventType,
                                                 String eventName, String crashFieldsPath) {
        return new CrashDataParams(eventId, appId, os, eventType, eventName, crashFieldsPath, null);
    }

    public static CrashDataParams libraryCrashParams(long eventId, int appId, String os, AppEventType eventType,
                                                     String crashFieldsPath, String libraryCrashFieldsPath) {
        return new CrashDataParams(eventId, appId, os, eventType, null, crashFieldsPath, libraryCrashFieldsPath);
    }
}
