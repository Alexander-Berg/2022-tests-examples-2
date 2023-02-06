package ru.yandex.metrika.util.dao;

import java.util.Calendar;
import java.util.Date;

import org.joda.time.DateTime;
import org.joda.time.DateTimeConstants;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

public class JodaDateTimePropertyConverterTest {

    private final JodaDateTimePropertyConverter jodaDateTimePropertyConverter = new JodaDateTimePropertyConverter();

    private Date date;
    private DateTime dateTime;

    @Before
    public void init() {
        Calendar calendar = Calendar.getInstance();
        calendar.set(2017, Calendar.AUGUST, 9, 14, 22, 42);
        calendar.set(Calendar.MILLISECOND, 123);
        date = calendar.getTime();

        dateTime = new DateTime(2017, DateTimeConstants.AUGUST, 9, 14, 22, 42, 123);
    }

    @Test
    public void testConvertToJdbc() {
        Assert.assertEquals(date, jodaDateTimePropertyConverter.convertToJdbc(dateTime));
    }

    @Test
    public void testConvertFromJdbc() {
        Assert.assertEquals(dateTime, jodaDateTimePropertyConverter.convertFromJdbc(date));
    }
}
