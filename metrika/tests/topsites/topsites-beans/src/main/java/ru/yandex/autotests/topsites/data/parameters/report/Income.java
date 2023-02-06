package ru.yandex.autotests.topsites.data.parameters.report;

public enum Income {

    A,
    B,
    C1,
    C2;

    @Override
    public String toString() {
        return name().toLowerCase();
    }
}
