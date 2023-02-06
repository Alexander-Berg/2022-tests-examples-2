package ru.yandex.autotests.tuneapitests.utils;

/**
 * User: alex89
 * Date: 30.08.12
 * geo-id регионов
 */

public enum Region {
    SPB("2", "Санкт-Петербург"),
    PSKOV("25", "псков"),
    GOMEL("155", "Гомель"),
    BREST("153", "Брест"),
    ODESSA("145", "Одесса"),
    LVOV("144", "Львов"),
    ALMATA("162", "Алмата"),
    KARAGANDA("164", "Караганда");

    private final String regionId;
    private final String regionName;

    Region(String regionId, String regionName) {
        this.regionId = regionId;
        this.regionName = regionName;
    }

    public String getRegionId() {
        return regionId;
    }

    public String getRegionName() {
        return regionName;
    }

    @Override
    public String toString() {
        return super.toString() + "(" + regionId + ")";
    }
}
