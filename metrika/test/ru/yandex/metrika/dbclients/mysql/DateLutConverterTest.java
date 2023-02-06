package ru.yandex.metrika.dbclients.mysql;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

import org.junit.Assert;
import org.junit.Test;

/** @author Artur Suilin */
public class DateLutConverterTest {

    @Test
    public void test() {
        DateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        DateLutConverter converter = new DateLutConverter(1, 1);
        Calendar c = Calendar.getInstance();
        int year = c.get(Calendar.YEAR);
        String s1 = (year + 1) + "-12-31 23:59:59";
        Date d1 = converter.toDate(s1);
        Assert.assertEquals(s1, df.format(d1));

        String s2 = (year - 1) + "-01-01 00:00:00";
        Date d2 = converter.toDate(s2);
        Assert.assertEquals(s2, df.format(d2));
        //System.out.println(d.toDate("2011-02-31 00:00:00"));

    }
}
