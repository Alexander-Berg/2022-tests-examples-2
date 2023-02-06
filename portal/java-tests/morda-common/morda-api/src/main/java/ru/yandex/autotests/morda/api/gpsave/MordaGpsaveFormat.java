package ru.yandex.autotests.morda.api.gpsave;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 30/05/16
 */
public enum MordaGpsaveFormat {
    JSON("json"),
    JSONP("jsonp"),
    XML("xml");

    private String value;

    MordaGpsaveFormat(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
