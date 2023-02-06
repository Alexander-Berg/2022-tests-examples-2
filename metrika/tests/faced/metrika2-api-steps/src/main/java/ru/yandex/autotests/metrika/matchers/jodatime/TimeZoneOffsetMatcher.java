package ru.yandex.autotests.metrika.matchers.jodatime;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import org.joda.time.DateTime;

/**
 * @author zgmnkv
 */
public class TimeZoneOffsetMatcher extends TypeSafeMatcher<DateTime> {

    private Matcher<Integer> offsetMatcher;

    public TimeZoneOffsetMatcher(Matcher<Integer> offsetMatcher) {
        this.offsetMatcher = offsetMatcher;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("a date time with time zone offset which is ")
                .appendDescriptionOf(offsetMatcher);
    }

    @Override
    protected boolean matchesSafely(DateTime item) {
        return offsetMatcher.matches(item.getZone().getOffset(item));
    }
}
