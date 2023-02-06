package ru.yandex.metrika.util.time;

import java.util.Date;

import org.junit.Ignore;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

/**
 * http://www.rg.ru/2014/07/25/vremiya-dok.html
 */
@Ignore("работает только в мск")
public class FZ248Test {

    public static final long THE_FIFTH_OF_NOVEMBER = 1415200000000L;

    @Test
    public void testJdk() {
        // not patched version
        /*
        orantius@orantius-e6320:~$ /usr/lib/jvm/java-8-oracle/bin/java -version
        java version "1.8.0_05"
        Java(TM) SE Runtime Environment (build 1.8.0_05-b13)
        Java HotSpot(TM) 64-Bit Server VM (build 25.5-b02, mixed mode)
        */
        // assertEquals("Wed Nov 05 19:06:40 MSK 2014", new Date(THE_FIFTH_OF_NOVEMBER).toString());
        /**
         * http://www.oracle.com/technetwork/java/javase/downloads/tzupdater-download-513681.html

         before
         orantius@orantius-e6320:~/dev/projects/joda/tzupdater-1.4.7-2014g$ java -jar tzupdater.jar --version
         tzupdater version 1.4.7-b01
         JRE time zone data version: tzdata2013h
         Embedded time zone data version: tzdata2014g

         orantius@orantius-e6320:~/dev/projects/joda/tzupdater-1.4.7-2014g$ sudo /usr/lib/jvm/java-8-oracle/java -jar tzupdater.jar -u

         after
         orantius@orantius-e6320:~/dev/projects/joda/tzupdater-1.4.7-2014g$ java -jar tzupdater.jar --version
         tzupdater version 1.4.7-b01
         JRE time zone data version: tzdata2014g
         Embedded time zone data version: tzdata2014g

         */
        assertEquals("Wed Nov 05 18:06:40 MSK 2014", new Date(THE_FIFTH_OF_NOVEMBER).toString());
    }

    @Test
    public void testJoda() {
        /*
        <dependency org="joda-time" name="joda-time" rev="2.3" transitive="false" />
        <dependency org="joda-time" name="joda-time" rev="2.4" transitive="false" />
        */
        //assertEquals("2014-11-05 19:06:40", DateTimeFormatters.MYSQL_DTF.print(THE_FIFTH_OF_NOVEMBER));
        /*
        <dependency org="joda-time" name="joda-time" rev="2.4.tz-patched" transitive="false" />
        */
        assertEquals("2014-11-05 18:06:40", DateTimeFormatters.MYSQL_DTF.print(THE_FIFTH_OF_NOVEMBER));
    }

    public void testMysql() {
        // SELECT FROM_UNIXTIME(1415200000) = '2014-11-05 19:06:40' AS FAIL
    }

    public void testClickhouse() {
//    orantius@mtlog01-01-1:~$ clickhouse-client --query 'select toDateTime(1415200000)'
//            2014-11-05 19:06:40
    }
}
