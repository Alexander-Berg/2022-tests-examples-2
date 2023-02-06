package ru.yandex.autotests.metrika.appmetrica.parameters;


/**
 * Признак того использовать ли при вычислениях время на устройстве или время на сервере
 */
public enum DateDimension {

    DEFAULT(null),
    RECEIVE("Receive");

    private final String value;

    DateDimension(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
