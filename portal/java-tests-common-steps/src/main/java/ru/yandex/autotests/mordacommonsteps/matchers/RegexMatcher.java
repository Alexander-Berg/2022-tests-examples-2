package ru.yandex.autotests.mordacommonsteps.matchers;

import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01.04.13
 */
public class RegexMatcher extends TypeSafeMatcher<String> {
    private final String regex;

    public RegexMatcher(String regex) {
        this.regex = regex;
    }

    @Override
    protected boolean matchesSafely(String s) {
        return s.matches(regex);
    }

    public void describeTo(Description description) {
        description.appendText(regex);
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        mismatchDescription.appendText("Строка ").appendValue(item).appendText(" не удовлетворяет шаблону ")
                .appendValue(regex);
    }

    public static RegexMatcher matches(String regex) {
        return new RegexMatcher(regex);
    }
}