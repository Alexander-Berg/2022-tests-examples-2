package ru.yandex.taxi.dmp.flink.utils;

import java.time.format.DateTimeFormatter;

import org.junit.jupiter.api.Test;

public class DateTimeUtilsTest {
    @Test
    public void testGetTimestampFromDateTimeWithOffset() throws Exception {
        var updatedString = "2021-08-10T14:55:18.227311749+03:00";
        var updated2String = "2021-08-10T11:55:18.227Z";
        var updatedAt = DateTimeUtils.getTimestampFromDateTimeWithOffset(updatedString,
                DateTimeFormatter.ISO_OFFSET_DATE_TIME);
        var updated2At = DateTimeUtils.getTimestampFromDateTimeWithOffset(updated2String,
                DateTimeFormatter.ISO_OFFSET_DATE_TIME);
        System.out.println(updatedAt);
        System.out.println(updated2At);
    }
    @Test
    public void testGetTimestampFromDateTimeUTC() throws Exception {
        var updatedString = "2021-08-11 12:56:21.206000".substring(0, 19);
        var updatedAt = DateTimeUtils.getTimestampFromDateTimeUTC(updatedString, DateTimeUtils.DATE_TIME);
        System.out.println(updatedAt);
    }

    @Test
    public void testGetDateTimeFromTimestamp() throws Exception {
        long updatedAt = 1628596518227L;
        var updatedAtString = DateTimeUtils.getDateTimeFromTimestampUTC(updatedAt,
                DateTimeFormatter.ISO_OFFSET_DATE_TIME);
        System.out.println(updatedAtString);
    }
}
