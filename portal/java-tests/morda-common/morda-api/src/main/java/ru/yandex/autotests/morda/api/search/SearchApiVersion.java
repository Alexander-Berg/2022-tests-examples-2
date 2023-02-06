package ru.yandex.autotests.morda.api.search;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21/11/16
 */
public enum SearchApiVersion {
    v1("1"),
    v2("2");

    private String value;

    SearchApiVersion(String value) {
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
