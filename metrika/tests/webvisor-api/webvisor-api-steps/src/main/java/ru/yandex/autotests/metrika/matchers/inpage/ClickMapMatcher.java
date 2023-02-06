package ru.yandex.autotests.metrika.matchers.inpage;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataClickGETSchema;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;

/**
 * Created by vananos on 07.10.16.
 */
public class ClickMapMatcher extends TypeSafeMatcher<MapsV1DataClickGETSchema> {
    private Matcher dataMatcher;
    private Throwable matchingException;

    public ClickMapMatcher(Matcher dataMatcher) {
        this.dataMatcher = dataMatcher;
    }

    @Override
    protected boolean matchesSafely(MapsV1DataClickGETSchema item) {
        boolean result;

        try {
            result = dataMatcher.matches(item.getData().getData());
        } catch (Throwable e) {
            result = false;
            matchingException = e;
        }

        return result;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("data is ")
                .appendDescriptionOf(dataMatcher).toString();
    }

    @Override
    protected void describeMismatchSafely(MapsV1DataClickGETSchema item, Description mismatchDescription) {
        if (matchingException == null) {
            try {
                mismatchDescription.appendText("data ");
                dataMatcher.describeMismatch(item.getData().getData(), mismatchDescription);
            } catch (Throwable e) {
                mismatchDescription.appendText("exception while describing mismatch ")
                        .appendValue(e);
            }
        } else {
            mismatchDescription.appendText("exception while matching ")
                    .appendValue(matchingException);
        }
    }

    public static Matcher expectNotEmpty() {
        return new ClickMapMatcher(not(empty()));
    }
}
