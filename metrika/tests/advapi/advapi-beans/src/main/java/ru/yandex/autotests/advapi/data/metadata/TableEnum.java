package ru.yandex.autotests.advapi.data.metadata;

import java.util.stream.Stream;

/**
 * Created by konkov on 05.08.2014.
 * Перечисление таблиц
 */
public enum TableEnum {
    EVENTS("am:e:");

    private final String namespace;

    TableEnum(String namespace) {
        this.namespace = namespace;
    }

    public String getValue() {
        return name().toLowerCase();
    }

    public String getNamespace() {
        return namespace;
    }

    @Override
    public String toString() {
        return getValue();
    }

    public static Stream<TableEnum> stream() {
        return Stream.of(values());
    }
}
