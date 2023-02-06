package ru.yandex.autotests.topsites.data.parameters.report;

public enum Age {

    AGE_0_17,
    AGE_18_24,
    AGE_25_34,
    AGE_35_44,
    AGE_45_54,
    AGE_55_PLUS;

    @Override
    public String toString() {
        return name().toLowerCase();
    }
}
