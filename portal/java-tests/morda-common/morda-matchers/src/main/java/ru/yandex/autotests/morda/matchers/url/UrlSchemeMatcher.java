package ru.yandex.autotests.morda.matchers.url;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import java.net.URI;

import static org.hamcrest.Matchers.equalTo;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16/08/16
 */
public class UrlSchemeMatcher extends TypeSafeMatcher<String> {

    private Matcher<String> schemeMatcher;
    private String scheme;

    public UrlSchemeMatcher(String scheme) {
        this(equalTo(normalize(scheme)));
    }

    public UrlSchemeMatcher(Matcher<String> schemeMatcher) {
        this.schemeMatcher = schemeMatcher;
    }

    public static UrlSchemeMatcher scheme(String scheme) {
        return new UrlSchemeMatcher(scheme);
    }

    public static UrlSchemeMatcher scheme(Matcher<String> schemeMatcher) {
        return new UrlSchemeMatcher(schemeMatcher);
    }

    private static String normalize(String scheme) {
        return scheme.toLowerCase();
    }

    @Override
    protected boolean matchesSafely(String item) {
        scheme = URI.create(item).getScheme();
        return schemeMatcher.matches(scheme) || schemeMatcher.matches(normalize(scheme));
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("scheme ")
                .appendDescriptionOf(schemeMatcher);
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        mismatchDescription.appendText("scheme was \"")
                .appendText(scheme)
                .appendText("\"");
    }
}
