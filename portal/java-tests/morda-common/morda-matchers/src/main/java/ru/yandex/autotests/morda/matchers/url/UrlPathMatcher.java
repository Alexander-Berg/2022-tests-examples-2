package ru.yandex.autotests.morda.matchers.url;

import org.apache.commons.lang3.StringUtils;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import java.net.URI;

import static org.hamcrest.Matchers.equalTo;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16/08/16
 */
public class UrlPathMatcher extends TypeSafeMatcher<String> {

    private Matcher<String> pathMatcher;
    private String path;

    public UrlPathMatcher(String path) {
        this(equalTo(normalize(path)));
    }

    public UrlPathMatcher(Matcher<String> pathMatcher) {
        this.pathMatcher = pathMatcher;
    }

    public static UrlPathMatcher path(String path) {
        return new UrlPathMatcher(path);
    }

    public static UrlPathMatcher path(Matcher<String> pathMatcher) {
        return new UrlPathMatcher(pathMatcher);
    }

    private static String normalize(String path) {
        return StringUtils.strip(path, "/");
    }

    @Override
    protected boolean matchesSafely(String item) {
        path = URI.create(item).getPath();
        return pathMatcher.matches(path) || pathMatcher.matches(normalize(path));
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("path ")
                .appendDescriptionOf(pathMatcher);
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        mismatchDescription.appendText("path was \"")
                .appendText(normalize(path))
                .appendText("\"");
    }
}
