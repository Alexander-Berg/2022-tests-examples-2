package ru.yandex.metrika.test.matchers;

import java.util.Optional;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

public class MoreMatchers {

    public static <T> Matcher<Optional<T>> isPresent() {
        return new TypeSafeMatcher<>() {
            @Override
            protected boolean matchesSafely(Optional<T> item) {
                return item.isPresent();
            }

            @Override
            public void describeTo(Description description) {
                description.appendText("Expected to have value but was empty");
            }
        };
    }

    public static <T> Matcher<Optional<T>> isEmpty() {
        return new TypeSafeMatcher<>() {
            @Override
            protected boolean matchesSafely(Optional<T> item) {
                return item.isEmpty();
            }

            @Override
            public void describeTo(Description description) {
                description.appendText("Expected to be empty but had value");
            }
        };
    }
}
