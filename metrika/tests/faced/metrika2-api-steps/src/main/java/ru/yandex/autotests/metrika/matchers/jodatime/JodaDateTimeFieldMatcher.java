package ru.yandex.autotests.metrika.matchers.jodatime;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import org.joda.time.DateTimeFieldType;
import org.joda.time.field.AbstractReadableInstantFieldProperty;

/**
 * @author zgmnkv
 */
public abstract class JodaDateTimeFieldMatcher<T> extends TypeSafeMatcher<T> {

    private DateTimeFieldType fieldType;
    private Matcher<Integer> fieldMatcher;

    public JodaDateTimeFieldMatcher(DateTimeFieldType fieldType, Matcher<Integer> fieldMatcher) {
        this.fieldType = fieldType;
        this.fieldMatcher = fieldMatcher;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("a ")
                .appendText(dateTimeType())
                .appendText(" with field ")
                .appendText(fieldType.getName())
                .appendText(" which is ")
                .appendDescriptionOf(fieldMatcher);
    }

    @Override
    protected boolean matchesSafely(T item) {
        return fieldMatcher.matches(getProperty(item, fieldType).get());
    }

    protected abstract String dateTimeType();

    protected abstract AbstractReadableInstantFieldProperty getProperty(T item, DateTimeFieldType fieldType);
}
