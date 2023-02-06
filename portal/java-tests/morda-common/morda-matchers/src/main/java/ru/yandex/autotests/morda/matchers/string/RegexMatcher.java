package ru.yandex.autotests.morda.matchers.string;

import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;

import java.util.regex.Pattern;

import static java.lang.String.format;

public class RegexMatcher extends TypeSafeMatcher<String> {
    private final Pattern pattern;

    public RegexMatcher(String regex) {
        this(Pattern.compile(regex));
    }

    public RegexMatcher(Pattern pattern) {
        this.pattern = pattern;
    }

    public static RegexMatcher regex(String regex) {
        return new RegexMatcher(regex);
    }

    public static RegexMatcher regex(String regex, Object... params) {
        return new RegexMatcher(format(regex, params));
    }

    public static RegexMatcher regex(Pattern pattern) {
        return new RegexMatcher(pattern);
    }

    @Override
    protected boolean matchesSafely(String s) {
        return pattern.matcher(s).matches();
    }

    public void describeTo(Description description) {
        description.appendText("/")
                .appendText(pattern.pattern())
                .appendText("/");
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        mismatchDescription.appendText("was ")
                .appendText(item);
    }
}