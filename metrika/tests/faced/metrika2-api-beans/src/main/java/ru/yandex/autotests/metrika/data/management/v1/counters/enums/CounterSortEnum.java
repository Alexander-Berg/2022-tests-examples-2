package ru.yandex.autotests.metrika.data.management.v1.counters.enums;

/**
 * Created by konkov on 18.08.2015.
 */
public enum CounterSortEnum {

    NONE("None"),
    DEFAULT("Default"),
    VISITS("Visits"),
    HITS("Hits"),
    UNIQUES("Uniques"),
    NAME("Name");

    private final String value;

    CounterSortEnum(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }

    @Override
    public String toString() {
        return getValue();
    }
}
