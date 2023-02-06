package ru.yandex.autotests.widgets.matchers;

import org.hamcrest.Factory;
import org.hamcrest.core.SubstringMatcher;

/**
 * User: ivannik
 * Date: 02.08.13
 * Time: 17:16
 */
public class StringContainsIgnoreCase extends SubstringMatcher {
    protected StringContainsIgnoreCase(String substring) {
        super(substring);
    }

    @Override
    protected boolean evalSubstringOf(String string) {
        return string.toLowerCase().contains(string.toLowerCase());
    }

    @Override
    protected String relationship() {
        return "containing";
    }

    @Factory
    public static StringContainsIgnoreCase containsIgnoreCase(String substring) {
        return new StringContainsIgnoreCase(substring);
    }
}
