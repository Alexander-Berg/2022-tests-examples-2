package ru.yandex.autotests.topsites.data.parameters.report;

public enum DeviceCategory {

    PC,
    MOBILE,
    TABLET;

    @Override
    public String toString() {
        return name().toLowerCase();
    }
}
