package ru.yandex.autotests.metrika.matchers;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeDiagnosingMatcher;
import org.hamcrest.core.IsAnything;

import java.util.List;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

/**
 * эмулятор цикла на матчерах.
 * матчер, в котором живет 0..size-1 (разных)матчеров, которые применяются к 0..size-1 элементам поступающего списка соответственно.
 *
 * @param <T>
 */
public class ListMatchers<T> extends TypeSafeDiagnosingMatcher<List<T>> {

    private final List<Matcher<T>> matchers;
    private final boolean failFast;

    public ListMatchers(int count, Function<Integer, Matcher<T>> generator) {
        this(count, generator, false);
    }

    public ListMatchers(int count, Function<Integer, Matcher<T>> generator, boolean failFast) {
        this(count, i -> true, generator, failFast);
    }

    public ListMatchers(int count, Predicate<Integer> assumption, Function<Integer, Matcher<T>> generator) {
        this(count, assumption, generator, false);
    }

    public ListMatchers(int count, Predicate<Integer> assumption, Function<Integer, Matcher<T>> generator, boolean failFast) {
        this(IntStream.range(0, count).mapToObj(i -> {
            if (assumption.test(i)) {
                return generator.apply(i);
            } else {
                return new IsAnything<T>();
            }
        }).collect(Collectors.toList()), failFast);
    }

    public ListMatchers(List<Matcher<T>> matchers, boolean failFast) {
        this.matchers = matchers;
        this.failFast = failFast;
    }


    @Override
    protected boolean matchesSafely(List<T> item, Description mismatchDescription) {
        if (item.size() != matchers.size()) {
            mismatchDescription.appendValue("matchers.size is " + matchers.size() + " but items.size is " + item.size());
            return false;
        }
        boolean failed = false;
        for (int i = 0; i < item.size(); i++) {
            if (!matchers.get(i).matches(item.get(i))) {
                mismatchDescription.appendText("" + i + ":");
                matchers.get(i).describeMismatch(item.get(i), mismatchDescription);
                mismatchDescription.appendText(" ");
                if (failFast) {
                    return false;
                } else {
                    failed = true;
                }
            }
        }
        return !failed;
    }

    @Override
    public void describeTo(Description description) {
        description.appendList("[", ",", "]", matchers);
    }
}
