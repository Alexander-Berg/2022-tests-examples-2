package ru.yandex.autotests.morda.matchers;

import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.Matcher;
import org.hamcrest.StringDescription;
import org.hamcrest.TypeSafeMatcher;

import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/01/15
 */
public class CollectionWithItemsDetailedMatcher<T> extends TypeSafeMatcher<List<T>> {
    private List<Matcher<T>> matchers;
    private Description describeMismatch;

    public CollectionWithItemsDetailedMatcher(List<Matcher<T>> matchers) {
        this.matchers = matchers;
        this.describeMismatch = new StringDescription().appendText("\n");
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("\n");
        for (int i = 0; i < matchers.size(); i++) {
            description.appendText("item [" + i + "]:\n");
            matchers.get(i).describeTo(description);
            description.appendText("\n");
        }
    }

    @Override
    protected boolean matchesSafely(List<T> t) {
        this.describeMismatch = new StringDescription().appendText("\n");
        boolean matches = true;

        if (matchers.size() != t.size()) {
            matches = false;
            describeMismatch.appendText("Expected " + matchers.size() + " items, was " + t.size() + "\n\n");
        }

        for (int i = 0; i < Math.min(matchers.size(), t.size()); i++) {
            if (!matchers.get(i).matches(t.get(i))) {
                matches = false;
                describeMismatch.appendText("item [" + i + "]:");
                matchers.get(i).describeMismatch(t.get(i), describeMismatch);
                describeMismatch.appendText("\n");
            }
        }

        return matches;
    }

    public CollectionWithItemsDetailedMatcher<T> and(Matcher<T>... matchers) {
        this.matchers.addAll(asList(matchers));
        return this;
    }

    @Override
    protected void describeMismatchSafely(List<T> item, Description mismatchDescription) {
        mismatchDescription.appendText(this.describeMismatch.toString());
    }

    @Factory
    public static <T> CollectionWithItemsDetailedMatcher<T> hasItemsDetailed(List<Matcher<T>> matchers) {
        return new CollectionWithItemsDetailedMatcher<T>(matchers);
    }

//    @Factory
//    @SafeVarargs
//    public static <T> Matcher<List<T>> hasItemsDetailed(Matcher<? super T>... matchers) {
//        return new CollectionHasItemsDetailedMatcher<>(matchers);
//    }
}
