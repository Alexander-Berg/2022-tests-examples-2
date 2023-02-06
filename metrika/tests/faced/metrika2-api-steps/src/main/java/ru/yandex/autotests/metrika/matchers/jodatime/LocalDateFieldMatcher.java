package ru.yandex.autotests.metrika.matchers.jodatime;

import org.hamcrest.Matcher;
import org.joda.time.DateTimeFieldType;
import org.joda.time.LocalDate;
import org.joda.time.field.AbstractReadableInstantFieldProperty;

/**
 * @author zgmnkv
 */
public class LocalDateFieldMatcher extends JodaDateTimeFieldMatcher<LocalDate> {

    public LocalDateFieldMatcher(DateTimeFieldType fieldType, Matcher<Integer> fieldMatcher) {
        super(fieldType, fieldMatcher);
    }

    @Override
    protected String dateTimeType() {
        return "local date";
    }

    @Override
    protected AbstractReadableInstantFieldProperty getProperty(LocalDate item, DateTimeFieldType fieldType) {
        return item.property(fieldType);
    }
}
