package ru.yandex.autotests.metrika.matchers;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import static org.apache.commons.lang3.StringUtils.chomp;
import static org.apache.commons.lang3.StringUtils.removeEnd;

/**
 * Created by konkov on 26.05.2015.
 */
public class IgnoreTrailingSlashMatcher extends TypeSafeMatcher<String> {

    private static final String SLASH = "/";
    private final String expected;

    public IgnoreTrailingSlashMatcher(String expected) {
        this.expected = removeEnd(expected, SLASH);
    }

    @Override
    protected boolean matchesSafely(String item) {
        return removeEnd(item, SLASH).equals(expected);
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("expected ")
                .appendValue(expected)
                .appendText(" with optional trailing slash");
    }

    public static Matcher<String> equalToIgnoringTrailingSlash(String expected) {
        return new IgnoreTrailingSlashMatcher(expected);
    }
}
