package ru.yandex.autotests.metrika.matchers.jodatime;

import org.hamcrest.Matcher;
import org.joda.time.DateTimeFieldType;
import org.joda.time.LocalDateTime;
import org.joda.time.field.AbstractReadableInstantFieldProperty;

/**
 * @author zgmnkv
 */
public class LocalDateTimeFieldMatcher extends JodaDateTimeFieldMatcher<LocalDateTime> {

    public LocalDateTimeFieldMatcher(DateTimeFieldType fieldType, Matcher<Integer> fieldMatcher) {
        super(fieldType, fieldMatcher);
    }

    @Override
    protected String dateTimeType() {
        return "local date time";
    }

    @Override
    protected AbstractReadableInstantFieldProperty getProperty(LocalDateTime item, DateTimeFieldType fieldType) {
        return item.property(fieldType);
    }
}
