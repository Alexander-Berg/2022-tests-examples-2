package ru.yandex.autotests.topsites.data.parameters.report;

public enum Gender {

    MALE,
    FEMALE;

    @Override
    public String toString() {
        return name().toLowerCase();
    }
}
