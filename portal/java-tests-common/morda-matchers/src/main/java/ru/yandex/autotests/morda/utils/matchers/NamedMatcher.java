package ru.yandex.autotests.morda.utils.matchers;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

public class NamedMatcher<T> extends TypeSafeMatcher<T> {

    protected String name;
    protected Matcher<T> matcher;

    public NamedMatcher(String name, Matcher<T> value) {
        this.name = name;
        this.matcher = value;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Matcher<T> getMatcher() {
        return matcher;
    }

    public void setMatcher(Matcher<T> matcher) {
        this.matcher = matcher;
    }

    @Override
    protected boolean matchesSafely(T item) {
        return matcher.matches(item);
    }

    @Override
    public void describeTo(Description description) {
        matcher.describeTo(description.appendText("\"" + name + "\": "));
    }

    @Override
    protected void describeMismatchSafely(T item, Description mismatchDescription) {
        matcher.describeMismatch(item, mismatchDescription.appendText("\"" + name + "\" "));
    }
}