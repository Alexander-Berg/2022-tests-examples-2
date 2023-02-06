package ru.yandex.autotests.metrika.matchers.jodatime;

import org.hamcrest.Matcher;
import org.joda.time.DateTime;
import org.joda.time.DateTimeFieldType;
import org.joda.time.field.AbstractReadableInstantFieldProperty;

/**
 * @author zgmnkv
 */
public class DateTimeFieldMatcher extends JodaDateTimeFieldMatcher<DateTime> {

    public DateTimeFieldMatcher(DateTimeFieldType fieldType, Matcher<Integer> fieldMatcher) {
        super(fieldType, fieldMatcher);
    }

    @Override
    protected String dateTimeType() {
        return "date time";
    }

    @Override
    protected AbstractReadableInstantFieldProperty getProperty(DateTime item, DateTimeFieldType fieldType) {
        return item.property(fieldType);
    }
}
