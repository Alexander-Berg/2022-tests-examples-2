package ru.yandex.autotests.metrika.data.management.v1.counters.enums;

/**
 * Created by proxeter on 25.07.2014.
 */
public enum CounterStatusEnum {

    /**
     * Включен
     */
    ACTIVE("active"),
    DELETED("Deleted");

    private String value;

    CounterStatusEnum(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }

    @Override
    public String toString() {
        return value;
    }
}
