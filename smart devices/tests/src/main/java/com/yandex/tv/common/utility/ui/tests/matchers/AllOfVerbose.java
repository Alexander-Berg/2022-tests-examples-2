/*
 * Copyright 2022 Yandex LLC. All rights reserved.
 */

package com.yandex.tv.common.utility.ui.tests.matchers;

import org.hamcrest.Description;
import org.hamcrest.DiagnosingMatcher;
import org.hamcrest.Matcher;

import java.util.Arrays;


/**
 * It's a copy of <a href="https://github.com/hamcrest/JavaHamcrest/blob/master/hamcrest/src/main/java/org/hamcrest/core/AllOf.java">hamcrest class</a>
 * with minor addition for more verbose logging.
 *
 * Calculates the logical conjunction of multiple matchers. Evaluation is shortcut, so
 * subsequent matchers are not called if an earlier matcher returns <code>false</code>.
 */
public class AllOfVerbose<T> extends DiagnosingMatcher<T> {

    private final Iterable<Matcher<? super T>> matchers;

    private String message = null;

    @SafeVarargs
    public AllOfVerbose(Matcher<? super T> ... matchers) {
        this(Arrays.asList(matchers));
    }

    public AllOfVerbose(Iterable<Matcher<? super T>> matchers) {
        this.matchers = matchers;
    }

    @SafeVarargs
    public AllOfVerbose(String message, Matcher<? super T> ... matchers) {
        this(Arrays.asList(matchers));
        this.message = message;
    }

    @Override
    public boolean matches(Object o, Description mismatch) {
        for (Matcher<? super T> matcher : matchers) {
            if (!matcher.matches(o)) {
                mismatch.appendDescriptionOf(matcher).appendText(" ");
                matcher.describeMismatch(o, mismatch);
                return false;
            }
        }
        return true;
    }

    @Override
    public void describeTo(Description description) {
        if (message != null) {
            description.appendText(message).appendText(":\n");
        }
        description.appendList("(\n", ", and\n ", "\n)", matchers);
    }

    /**
     * Creates a matcher that matches if the examined object matches <b>ALL</b> of the specified matchers.
     * For example:
     * <pre>assertThat("myValue", allOf(startsWith("my"), containsString("Val")))</pre>
     */
    public static <T> Matcher<T> allOfVerbose(Iterable<Matcher<? super T>> matchers) {
        return new AllOfVerbose<>(matchers);
    }

    /**
     * Creates a matcher that matches if the examined object matches <b>ALL</b> of the specified matchers.
     * For example:
     * <pre>assertThat("myValue", allOf(startsWith("my"), containsString("Val")))</pre>
     */
    @SafeVarargs
    public static <T> Matcher<T> allOfVerbose(Matcher<? super T>... matchers) {
        return new AllOfVerbose<>(matchers);
    }

    /**
     * Creates a matcher that matches if the examined object matches <b>ALL</b> of the specified matchers.
     * For example:
     * <pre>assertThat("myValue", allOf(startsWith("my"), containsString("Val")))</pre>
     */
    @SafeVarargs
    public static <T> Matcher<T> allOfVerbose(String message, Matcher<? super T>... matchers) {
        return new AllOfVerbose<>(message, matchers);
    }
}
