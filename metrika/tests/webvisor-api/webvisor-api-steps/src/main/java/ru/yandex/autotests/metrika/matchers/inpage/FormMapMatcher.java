package ru.yandex.autotests.metrika.matchers.inpage;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataFormGETPOSTSchema;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;

/**
 * Created by vananos on 07.10.16.
 */
public class FormMapMatcher extends TypeSafeMatcher<MapsV1DataFormGETPOSTSchema> {
    private Matcher formMatcher;
    private Throwable matchingException;

    public FormMapMatcher(Matcher dataMatcher) {
        this.formMatcher = dataMatcher;
    }

    @Override
    protected boolean matchesSafely(MapsV1DataFormGETPOSTSchema item) {
        boolean result;

        try {
            result = formMatcher.matches(item.getForms());
        } catch (Throwable e) {
            result = false;
            matchingException = e;
        }

        return result;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("forms is ")
                .appendDescriptionOf(formMatcher).toString();
    }

    @Override
    protected void describeMismatchSafely(MapsV1DataFormGETPOSTSchema item, Description mismatchDescription) {
        if (matchingException == null) {
            try {
                mismatchDescription.appendText("forms ");
                formMatcher.describeMismatch(item.getForms(), mismatchDescription);
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
        return new FormMapMatcher(not(empty()));
    }
}
