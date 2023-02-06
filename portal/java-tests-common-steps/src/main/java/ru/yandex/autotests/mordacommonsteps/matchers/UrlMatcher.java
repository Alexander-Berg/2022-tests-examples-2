package ru.yandex.autotests.mordacommonsteps.matchers;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import org.openqa.selenium.WebDriver;

/**
 * User: eoff
 * Date: 14.02.13
 */
@Deprecated
public class UrlMatcher extends TypeSafeMatcher<WebDriver> {
    private Matcher<String> matcher;

    public UrlMatcher(Matcher<String> matcher) {
        this.matcher = matcher;
    }

    @Override
    protected boolean matchesSafely(WebDriver item) {
        return matcher.matches(item.getCurrentUrl());
    }

    @Override
    public void describeTo(Description description) {
        matcher.describeTo(description);
    }

    @Override
    protected void describeMismatchSafely(WebDriver item, Description mismatchDescription) {
        mismatchDescription.appendText("url: ").appendValue(item.getCurrentUrl());
    }

    public static UrlMatcher urlMatches(Matcher<String> matcher) {
        return new UrlMatcher(matcher);
    }
}
