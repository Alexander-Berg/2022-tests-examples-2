package ru.yandex.autotests.advapi.data.metadata;

/**
 * Created by konkov on 28.09.2015.
 */
public enum SubTable {
    NONE(null),
    ECART("ECart"),
    EPURCHASE("EPurchase"),
    EACTION("EAction");

    private final String name;

    SubTable(String name) {
        this.name = name;
    }

    public String getValue() {
        return name;
    }

    @Override
    public String toString() {
        return getValue();
    }
}
