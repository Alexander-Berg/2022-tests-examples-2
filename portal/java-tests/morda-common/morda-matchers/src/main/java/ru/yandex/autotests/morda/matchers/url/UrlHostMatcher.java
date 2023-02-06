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
public class UrlHostMatcher extends TypeSafeMatcher<String> {

    private Matcher<String> hostMatcher;
    private String host;

    public UrlHostMatcher(String host) {
        this(equalTo(normalize(host)));
    }

    public UrlHostMatcher(Matcher<String> hostMatcher) {
        this.hostMatcher = hostMatcher;
    }

    public static UrlHostMatcher host(String host) {
        return new UrlHostMatcher(host);
    }

    public static UrlHostMatcher host(Matcher<String> hostMatcher) {
        return new UrlHostMatcher(hostMatcher);
    }

    private static String normalize(String host) {
        return host.toLowerCase();
    }

    @Override
    protected boolean matchesSafely(String item) {
        host = URI.create(item).getHost().toLowerCase();
        return hostMatcher.matches(host) || hostMatcher.matches(normalize(host));
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("host ")
                .appendDescriptionOf(hostMatcher);
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        mismatchDescription.appendText("host was \"")
                .appendText(host)
                .appendText("\"");
    }
}
