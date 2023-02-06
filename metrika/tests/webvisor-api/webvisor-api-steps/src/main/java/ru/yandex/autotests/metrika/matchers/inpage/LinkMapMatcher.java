package ru.yandex.autotests.metrika.matchers.inpage;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataLinkMapGETSchema;
import ru.yandex.metrika.ui.maps.external.LinkMapResponseExternal;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;

/**
 * Created by vananos on 07.10.16.
 */
public class LinkMapMatcher extends TypeSafeMatcher<MapsV1DataLinkMapGETSchema> {
    private Matcher lMatcher;
    private Matcher tMatcher;
    private Throwable matchingException;

    public LinkMapMatcher(Matcher lMatcher, Matcher tMatcher) {
        this.lMatcher = lMatcher;
        this.tMatcher = tMatcher;
    }

    @Override
    protected boolean matchesSafely(MapsV1DataLinkMapGETSchema item) {
        boolean result;

        try {
            LinkMapResponseExternal data = item.getData();
            result = lMatcher.matches(data.getL().entrySet()) && tMatcher.matches(data.getT());
        } catch (Throwable e) {
            result = false;
            matchingException = e;
        }

        return result;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("L is ")
                .appendDescriptionOf(lMatcher)
                .appendText(" and T is ")
                .appendDescriptionOf(tMatcher)
                .toString();
    }

    @Override
    protected void describeMismatchSafely(MapsV1DataLinkMapGETSchema item, Description mismatchDescription) {
        if (matchingException == null) {
            try {
                LinkMapResponseExternal data = item.getData();
                mismatchDescription.appendText("L ");
                lMatcher.describeMismatch(data.getL().entrySet(), mismatchDescription);
                mismatchDescription.appendText(" and T ");
                tMatcher.describeMismatch(data.getT(), mismatchDescription);
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
        return new LinkMapMatcher(not(empty()), not(empty()));
    }
}
