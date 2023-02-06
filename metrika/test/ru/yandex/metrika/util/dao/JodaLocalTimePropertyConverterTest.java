package ru.yandex.metrika.util.dao;

import java.util.Calendar;
import java.util.Date;

import org.joda.time.LocalTime;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

public class JodaLocalTimePropertyConverterTest {

    private final JodaLocalTimePropertyConverter jodaLocalTimePropertyConverter = new JodaLocalTimePropertyConverter();

    private Date date;
    private LocalTime localTime;

    @Before
    public void init() {
        Calendar calendar = Calendar.getInstance();
        calendar.set(Calendar.HOUR_OF_DAY, 17);
        calendar.set(Calendar.MINUTE, 23);
        calendar.set(Calendar.SECOND, 42);
        calendar.set(Calendar.MILLISECOND, 0);
        date = calendar.getTime();

        localTime = new LocalTime(17, 23, 42);
    }

    @Test
    public void testConvertToJdbc() {
        Assert.assertEquals(date, jodaLocalTimePropertyConverter.convertToJdbc(localTime));
    }

    @Test
    public void testConvertFromJdbc() {
        Assert.assertEquals(localTime, jodaLocalTimePropertyConverter.convertFromJdbc(date));
    }
}
