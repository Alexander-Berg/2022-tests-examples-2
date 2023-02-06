package ru.yandex.autotests.mordacommonsteps.matchers;

import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.selectFirst;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28.11.13
 */
public class ListContainsElementMatcher<T, E> extends TypeSafeMatcher<List<? extends T>> {

    private T item;
    private E element;
    private Matcher<? super E> matcher;

    public ListContainsElementMatcher(E element, Matcher<? super E> matcher) {
        this.element = element;
        this.matcher = matcher;
    }

    @Override
    protected boolean matchesSafely(List<? extends T> item) {
        this.item = selectFirst(item, having(element, matcher));
        return this.item != null;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("list containing element that fits ").appendValue(matcher);
    }

    @Override
    protected void describeMismatchSafely(List<? extends T> item, Description mismatchDescription) {
        mismatchDescription.appendText("element that fits ").appendValue(matcher).appendText(" not found in list ")
                .appendValue(item);
    }

    @Factory
    public static <T, E> ListContainsElementMatcher<T, E> hasItem(E element, Matcher<? super E> list) {
        return new ListContainsElementMatcher<>(element, list);
    }

    public T getItem() {
        return item;
    }
}
