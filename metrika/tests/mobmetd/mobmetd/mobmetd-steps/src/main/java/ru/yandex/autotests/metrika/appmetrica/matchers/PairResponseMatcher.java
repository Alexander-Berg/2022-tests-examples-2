package ru.yandex.autotests.metrika.appmetrica.matchers;

import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

/**
 * Created by konkov on 31.07.2015.
 */
public class PairResponseMatcher<T extends Pair> extends TypeSafeMatcher<T> {

    private final Pair<Matcher, Matcher> matcherPair;
    private Throwable matchingException;

    public PairResponseMatcher(Matcher referenceMatcher, Matcher testingMatcher) {
        this.matcherPair = ImmutablePair.of(referenceMatcher, testingMatcher);
    }

    public PairResponseMatcher(Pair<Matcher, Matcher> referenceAndTestingMatcherPair) {
        this.matcherPair = referenceAndTestingMatcherPair;
    }

    @Override
    protected boolean matchesSafely(T item) {
        boolean result;

        try {
            result = matcherPair.getLeft().matches(item.getLeft()) & matcherPair.getRight().matches(item.getRight());
        } catch (Throwable e) {
            result = false;
            matchingException = e;
        }

        return result;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("reference: ")
                .appendDescriptionOf(matcherPair.getLeft())
                .appendText(" testing: ")
                .appendDescriptionOf(matcherPair.getRight());
    }

    @Override
    protected void describeMismatchSafely(T item, Description mismatchDescription) {
        if (matchingException == null) {
            try {
                mismatchDescription.appendText("reference: ");
                matcherPair.getLeft().describeMismatch(item.getLeft(), mismatchDescription);
                mismatchDescription.appendText(" testing: ");
                matcherPair.getRight().describeMismatch(item.getRight(), mismatchDescription);
            } catch (Throwable e) {
                mismatchDescription.appendText("exception while describing mismatch ")
                        .appendValue(e);
            }
        } else {
            mismatchDescription.appendText("exception while matching ")
                    .appendValue(matchingException);
        }
    }
}
