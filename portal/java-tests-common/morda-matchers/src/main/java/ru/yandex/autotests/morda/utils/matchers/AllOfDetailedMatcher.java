package ru.yandex.autotests.morda.utils.matchers;

import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.Matcher;
import org.hamcrest.StringDescription;
import org.hamcrest.TypeSafeMatcher;

import java.util.Arrays;
import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/01/15
 */
public class AllOfDetailedMatcher<T> extends TypeSafeMatcher<T> {
    private List<Matcher<? super T>> matchers;
    private Description describeMismatch;

    public AllOfDetailedMatcher(List<Matcher<? super T>> matchers) {
        this.matchers = matchers;
        this.describeMismatch = new StringDescription().appendText("\n");
    }

    @SafeVarargs
    public AllOfDetailedMatcher(Matcher<? super T>... matchers) {
        this(Arrays.asList(matchers));
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("\n");
        for (Matcher<? super T> matcher : matchers) {
            matcher.describeTo(description);
            description.appendText("\n");
        }
    }

    @Override
    protected boolean matchesSafely(T t) {
        this.describeMismatch = new StringDescription().appendText("\n");
        boolean matches = true;
        for (Matcher<? super T> matcher : matchers) {
            if (!matcher.matches(t)) {
                matches = false;
                matcher.describeMismatch(t, describeMismatch);
                describeMismatch.appendText("\n");
            }
        }
        return matches;
    }

    @Override
    protected void describeMismatchSafely(T item, Description mismatchDescription) {
        mismatchDescription.appendText(this.describeMismatch.toString());
    }

    @Factory
    public static <T> AllOfDetailedMatcher<T> allOfDetailed(List<Matcher<? super T>> matchers) {
        return new AllOfDetailedMatcher<>(matchers);
    }

    @Factory
    @SafeVarargs
    public static <T> AllOfDetailedMatcher<T> allOfDetailed(Matcher<? super T>... matchers) {
        return new AllOfDetailedMatcher<>(matchers);
    }
}
