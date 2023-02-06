package ru.yandex.autotests.metrika.matchers;

import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import org.joda.time.format.ISODateTimeFormat;

import java.util.IllegalFormatException;

/**
 * Created by konkov on 05.12.2014.
 * Матчер для проверки формата строки
 */
public class DateTimeFormatMatcher extends TypeSafeMatcher<String> {
    @Override
    protected boolean matchesSafely(String s) {
        try {
            ISODateTimeFormat.dateTimeParser().parseDateTime(s);
            return true;
        }
        catch (IllegalFormatException e) {
            return false;
        }
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("ожидается формат ISO8601");
    }

    @Factory
    public static Matcher<String> iso8601Format() {
        return new DateTimeFormatMatcher();
    }
}
