package ru.yandex.autotests.mainmorda.utils;

import org.hamcrest.Matcher;

/**
 * User: ivannik
 * Date: 18.06.2014
 */
public class LinkHrefInfo {
    public Matcher<String> text;
    public Matcher<String> href;

    public LinkHrefInfo(Matcher<String> text, Matcher<String> href) {
        this.text = text;
        this.href = href;
    }

    @Override
    public String toString() {
        return text.toString();
    }
}
