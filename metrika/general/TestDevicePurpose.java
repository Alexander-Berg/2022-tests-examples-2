package ru.yandex.metrika.mobmet.model;

/**
 * Назначение тестового устройства.
 * <p>
 * Created by graev on 12/07/16.
 */
public enum TestDevicePurpose {
    reattribution("reattribution"),
    push_notifications("push_notifications");

    private final String dbName;

    TestDevicePurpose(String dbName) {
        this.dbName = dbName;
    }

    public String getDbName() {
        return dbName;
    }
}
