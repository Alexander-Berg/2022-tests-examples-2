package ru.yandex.metrika.managers;

import org.joda.time.DateTimeZone;
import org.joda.time.format.DateTimeFormat;
import org.junit.Ignore;

/**
 *
 * org.joda.time.format.DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").withZone(org.joda.time.DateTimeZone.forID("Asia/Barnaul")).print(java.lang.System.currentTimeMillis()+86400000*4)
 * Created by orantius on 24.03.16.
 *
 *
 *
 */
/*
Thu Mar 24 19:46:42 GMT+03:00 2016:org.joda.time.format.DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").withZone(org.joda.time.DateTimeZone.forID("Asia/Barnaul")).print(java.lang.System.currentTimeMillis()+86400000*1) running time 26 ms.
2016-03-25 22:46:42
Thu Mar 24 19:46:09 GMT+03:00 2016:org.joda.time.format.DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").withZone(org.joda.time.DateTimeZone.forID("Asia/Barnaul")).print(java.lang.System.currentTimeMillis()+86400000*4) running time 38 ms.
2016-03-28 23:46:09

* */
    @Ignore
public class TimeZonesTest {
    public static void main(String[] args) {
        long today = System.currentTimeMillis();
        long l = today +86400*1000L*4;
        System.out.println(DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").withZone(DateTimeZone.forID("Asia/Barnaul")).print(l));
        System.out.println(DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").withZone(DateTimeZone.forID("Asia/Omsk")).print(l));


        System.out.println(DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").withZone(DateTimeZone.forID("Asia/Chita")).print(today));
        System.out.println(DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").withZone(DateTimeZone.forID("Asia/Chita")).print(l));
    }
}
