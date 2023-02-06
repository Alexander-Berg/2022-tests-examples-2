package ru.yandex.autotests.mordacommonsteps.utils;

/**
 * User: eoff
 * Date: 23.11.12
 */
public enum HtmlAttribute {
    HREF("href"),
    SRC("src"),
    TITLE("title"),
    ALT("alt"),
    VALUE("value"),
    SELECTED("selected"),
    STYLE("style"),
    CONTENT("content"),
    DATA_TYPE("data-type"),
    DATA_RELATIONSHIP("data-relationship"),
    CLASS("class"),
    WIDTH("width"),
    HEIGHT("height"),
    ID("id"),
    DATA_LOGIN("data-login"),
    ACTION("action"),
    PLACEHOLDER("placeholder"),
    DATA_ID("data-id"),
    DATA_KEY("data-key"),
    DATA_STAT_SELECT("data-stat-select"),
    DATA_STATLOG("data-statlog"),
    DATA_RUBR("data-rubr"),
    DATA_IMAGE("data-image"),
    DATA_LOGO_URL("data-logo-url"),
    ARIA_LABEL("aria-label");

    private String value;

    private HtmlAttribute(String value) {
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
