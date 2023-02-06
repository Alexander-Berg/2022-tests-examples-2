package ru.yandex.autotests.morda.matchers;

import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.Matcher;
import org.hamcrest.StringDescription;
import org.hamcrest.TypeSafeMatcher;

import java.util.ArrayList;
import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/01/15
 */
public class AllOfDetailedMatcher<T> extends TypeSafeMatcher<T> {
    private List<Matcher<? super T>> matchers;
    private Description describeMismatch;

    public AllOfDetailedMatcher(List<Matcher<? super T>> matchers) {
        this.matchers = new ArrayList<>(matchers);
        this.describeMismatch = new StringDescription().appendText("\n");
    }

    @Factory
    public static <T> AllOfDetailedMatcher<T> allOfDetailed(List<Matcher<? super T>> matchers) {
        return new AllOfDetailedMatcher<T>(matchers);
    }

    @Factory
    @SafeVarargs
    public static <T> AllOfDetailedMatcher<T> allOfDetailed(Matcher<? super T>... matchers) {
        return new AllOfDetailedMatcher<T>(asList(matchers));
    }

    public AllOfDetailedMatcher<T> and(Matcher<? super T>... matchers) {
        this.matchers.addAll(asList(matchers));
        return this;
    }

    @Override
    public void describeTo(Description description) {

        for (Matcher<? super T> matcher : matchers) {
            description.appendText("  ");
            matcher.describeTo(description);
            description.appendText("\n");
        }
    }

    @Override
    protected boolean matchesSafely(T t) {
        this.describeMismatch = new StringDescription();
        boolean matches = true;
        for (Matcher<? super T> matcher : matchers) {
            if (!matcher.matches(t)) {
                matches = false;
                describeMismatch.appendText("  ");
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
}
