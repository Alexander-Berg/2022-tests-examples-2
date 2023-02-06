package ru.yandex.autotests.tabcrunch;

import org.junit.Test;
import ru.yandex.autotests.tabcrunch.util.CSVSONLineParser;

import java.nio.charset.StandardCharsets;
import java.util.List;

import static junit.framework.Assert.assertEquals;

/**
 * Created by lonlylocly on 24.03.14.
 */
public class CSVSONTest {

    @Test
    public void csvsonUrlPrettifyTest(){
        final CSVSONLineParser lp = new CSVSONLineParser();
        lp.setPrettifyUrls(true);
        final List<String> s = lp.parseLine("\"http://auto.onliner.by/2014/02/20/kamery-24/\""
                .getBytes(StandardCharsets.UTF_8));

        assertEquals(s.get(0), "http://auto.onliner.by/2014/02/20/kamery-24");
    }


    @Test
    public void csvsonTest(){
        final CSVSONLineParser lp = new CSVSONLineParser();
        lp.setPrettifyUrls(true);
        String s = "5770612,\"2014-02-20\",12156600508678802921,2,{12:1, 13:2},\"http://forum.onliner.by/\",0,0";
        String expect = "\"5770612\",\"2014-02-20\",\"12156600508678802921\",\"2\",\"{\\\"12\\\":1,\\\"13\\\":2}\",\"http://forum.onliner.by\",\"0\",\"0\"";

        final List<String> ls = lp.parseLine(s.getBytes(StandardCharsets.UTF_8));
        String s2 = lp.joinLine(ls);

        assertEquals(expect, s2);
    }

}
