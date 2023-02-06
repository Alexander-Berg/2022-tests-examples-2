package ru.yandex.autotests.metrika.matchers.jodatime;

import org.hamcrest.Matcher;
import org.joda.time.DateTimeFieldType;
import org.joda.time.LocalTime;
import org.joda.time.field.AbstractReadableInstantFieldProperty;

/**
 * @author zgmnkv
 */
public class LocalTimeFieldMatcher extends JodaDateTimeFieldMatcher<LocalTime> {

    public LocalTimeFieldMatcher(DateTimeFieldType fieldType, Matcher<Integer> fieldMatcher) {
        super(fieldType, fieldMatcher);
    }

    @Override
    protected String dateTimeType() {
        return "local time";
    }

    @Override
    protected AbstractReadableInstantFieldProperty getProperty(LocalTime item, DateTimeFieldType fieldType) {
        return item.property(fieldType);
    }
}
