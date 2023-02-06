package ru.yandex.autotests.metrika.appmetrica.matchers;

import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;

import java.util.Comparator;

/**
 * Проверяет, что список отсортирован по определенному компаратору
 * <p>
 * Created by graev on 16/01/2017.
 */
public final class SortedByMatcher<T> extends TypeSafeMatcher<Iterable<T>>{

    private final Comparator<T> comparator;

    public static <T> SortedByMatcher<T> sortedBy(Comparator<T> comparator) {
        return new SortedByMatcher<>(comparator);
    }

    public SortedByMatcher(Comparator<T> comparator) {
        this.comparator = comparator;
    }

    @Override
    protected boolean matchesSafely(Iterable<T> list) {
        T last = null;
        boolean lastIsDefined = false;

        for (T element : list) {
            if (lastIsDefined && comparator.compare(last, element) > 0) {
                return false;
            } else {
                lastIsDefined = true;
            }

            last = element;
        }

        return true;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("list is sorted according to provided comparator");
    }
}
