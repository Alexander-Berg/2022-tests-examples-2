package ru.yandex.autotests.metrika.data.metadata.v1.enums;

import java.util.stream.Stream;

/**
 * Created by konkov on 05.08.2014.
 * Перечисление таблиц
 */
public enum TableEnum {
    HITS("ym:pv:"),
    VISITS("ym:s:"),
    EXTERNAL_LINKS("ym:el:"),
    DOWNLOADS("ym:dl:"),
    SHARE_SERVICES("ym:sh:"),
    SITE_SPEED("ym:sp:"),
    ADVERTISING("ym:ad:"),
    CLICKS("ym:c:"),
    CLICK_STORAGE("ym:cs:"),
    USER_PARAM("ym:up:"),
    EXPENSES_VISITS("ym:ev:");

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
    public String toString(){
        return getValue();
    }

    public static Stream<TableEnum> stream() {
        return Stream.of(values());
    }
}
