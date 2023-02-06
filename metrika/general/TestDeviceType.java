package ru.yandex.metrika.mobmet.model;

/**
 * Created by pavlyuklp on 24.11.2016.
 */
public enum TestDeviceType {
    appmetrica_device_id("appmetrica_device_id", "appmetrica_device_id"),
    ios_ifa("ios_ifa", "IDFA"),
    ios_ifv("ios_ifv", "IDFV"),
    google_aid("google_aid", "GAID"),
    windows_aid("windows_aid", "Microsoft Advertising ID"),
    huawei_oaid("huawei_oaid", "Huawei OAID");

    private final String dbName;
    private final String publicName;

    TestDeviceType(String dbName, String publicName) {
        this.dbName = dbName;
        this.publicName = publicName;
    }

    public String getDbName() {
        return dbName;
    }

    /**
     * Для сообщений пользователю.
     */
    public String getPublicName() {
        return publicName;
    }
}
