package ru.yandex.autotests.metrika.data.management.v1.counters.enums;

/**
 * Created by proxeter on 25.07.2014.
 */
public enum CounterTypeEnum {

    /**
     * Счетчик импортирован из РСЯ
     */
    PARTNER("partner"),

    /**
     * Счетчик создан пользователем в Яндекс.Метрике
     */
    SIMPLE("simple");

    private String value;

    CounterTypeEnum(String value) {
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
