package ru.yandex.autotests.metrika.matchers;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import java.util.Collection;

import static ru.yandex.autotests.metrika.utils.Utils.getDuplicates;

/**
 * Created by konkov on 25.07.2016.
 */
public class NoDuplicatesMatcher<T> extends TypeSafeMatcher<Iterable<? super T>> {

    private Collection<? super T> duplicates;

    @Override
    protected boolean matchesSafely(Iterable<? super T> item) {
        duplicates = getDuplicates(item);
        return duplicates.isEmpty();
    }

    @Override
    protected void describeMismatchSafely(Iterable<? super T> item, Description mismatchDescription) {
        mismatchDescription.appendText("обнаружены дубликаты ").appendValueList("[ ", ", ", " ]", duplicates);
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("дубликатов не содержит");
    }

    public static <T> Matcher<Iterable<? super T>> hasNoDuplicates() {
        return new NoDuplicatesMatcher<>();
    }
}
