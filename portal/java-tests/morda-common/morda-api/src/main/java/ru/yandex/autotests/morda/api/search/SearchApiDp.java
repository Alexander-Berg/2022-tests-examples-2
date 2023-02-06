package ru.yandex.autotests.morda.api.search;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 25/05/16
 */
public enum SearchApiDp {
    _1("1", 1),
    _1_5("1.5", 1.5),
    _2("2", 2),
    _3("3", 3),
    _4("4", 4);

    private String value;
    private double mult;

    SearchApiDp(String value, double mult) {
        this.value = value;
        this.mult = mult;
    }

    public String getValue() {
        return value;
    }

    public double getMult() {
        return mult;
    }

    @Override
    public String toString() {
        return value;
    }
}
