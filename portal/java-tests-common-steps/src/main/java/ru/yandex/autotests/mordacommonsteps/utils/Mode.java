package ru.yandex.autotests.mordacommonsteps.utils;

import org.hamcrest.Matcher;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.not;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19.04.13
 */
public enum Mode {
    PLAIN(not(containsString("b-page_widgets")), "Плоский режим", "Плоский режим не установлен!"),
    EDIT(containsString("b-page_setup"), "Режим редактирования", "Режим редактирования не установлен!"),
    FAKE(containsString("b-page_fake"), " Фейковый режим", "Фейковый режим не установлен!"),
    WIDGET(containsString("b-page_widgets"), "Виджетный режим", "Виджетный режим не установлен!");

    private Mode(Matcher<String> bodyMatcher, String textMatch, String textMismatch) {
        this.bodyMatcher = bodyMatcher;
        this.textMatch = textMatch;
        this.textMismatch = textMismatch;
    }

    private Matcher<String> bodyMatcher;
    private String textMatch;
    private String textMismatch;

    public Matcher<String> getBodyMatcher() {
        return bodyMatcher;
    }

    public String getTextMatch() {
        return textMatch;
    }

    public String getTextMismatch() {
        return textMismatch;
    }
}

