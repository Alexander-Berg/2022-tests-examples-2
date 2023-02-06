package ru.yandex.metrika.util.dao;

import java.util.Calendar;
import java.util.Date;

import org.joda.time.DateTimeConstants;
import org.joda.time.LocalDate;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

public class JodaLocalDatePropertyConverterTest {

    private final JodaLocalDatePropertyConverter jodaLocalDatePropertyConverter = new JodaLocalDatePropertyConverter();

    private Date date;
    private LocalDate localDate;

    @Before
    public void init() {
        Calendar calendar = Calendar.getInstance();
        calendar.set(2017, Calendar.AUGUST, 9, 0, 0, 0);
        calendar.set(Calendar.MILLISECOND, 0);
        date = calendar.getTime();

        localDate = new LocalDate(2017, DateTimeConstants.AUGUST, 9);
    }

    @Test
    public void testConvertToJdbc() {
        Assert.assertEquals(date, jodaLocalDatePropertyConverter.convertToJdbc(localDate));
    }

    @Test
    public void testConvertFromJdbc() {
        Assert.assertEquals(localDate, jodaLocalDatePropertyConverter.convertFromJdbc(date));
    }
}
