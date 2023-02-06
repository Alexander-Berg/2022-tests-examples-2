package ru.yandex.autotests.morda.api.search;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 25/05/16
 */
public enum SearchApiBlock {
    ALL(""),
    SEARCH("search"),
    AFISHA("afisha"),
    APPLICATION("application"),
    TV("tv"),
    VIDEO("video"),
    NOW("now"),
    TOPNEWS("topnews"),
    TRANSPORT("transport"),
    POI("poi"),
    BRIDGES("bridges"),
    INFORMER("informer"),
    WEATHER("weather"),
    SERVICES("services"),
    TRANSPORTMAP("transportmap"),
    STOCKS("stocks");

    private String value;

    SearchApiBlock(String value) {
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
