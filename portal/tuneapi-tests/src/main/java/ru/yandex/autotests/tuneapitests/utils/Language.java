package ru.yandex.autotests.tuneapitests.utils;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21/01/15
 */
public enum Language {
    RU("ru", "1"),
    UK("uk", "2"),
    EN("en", "3"),
    KK("kk", "4"),
    BE("be", "5"),
    TT("tt", "6"),
    AZ("az", "7"),
    TR("tr", "8"),
    HY("hy", "9"),
    KA("ka", "10"),
    RO("ro", "11");

    private String value;
    private String myValue;

    Language(String value, String myValue) {
        this.value = value;
        this.myValue = myValue;
    }

    public String getValue() {
        return value;
    }

    public String getMyValue() {
        return myValue;
    }
}
