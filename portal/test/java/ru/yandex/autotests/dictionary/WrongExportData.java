package ru.yandex.autotests.dictionary;

import org.junit.Test;
import ru.yandex.autotests.dictionary.cleaners.HomeCleaner;

/**
 * User: leonsabr
 * Date: 27.07.12
 */
public class WrongExportData {
    @Test(expected = IllegalArgumentException.class)
    public void test1() {
        new Tanker(getClass().getClassLoader().getResource("no.xml"));
    }

    @Test(expected = IllegalArgumentException.class)
    public void test2() {
        new Tanker(getClass().getClassLoader().getResource("no.xml"),
                getClass().getClassLoader().getResource("noagain.xml"));
    }

    @Test(expected = IllegalArgumentException.class)
    public void cleanerTest1() {
        new Tanker(new HomeCleaner(), getClass().getClassLoader().getResource("no.xml"));
    }

    @Test(expected = IllegalArgumentException.class)
    public void cleanerTest2() {
        new Tanker(new HomeCleaner(), getClass().getClassLoader().getResource("no.xml"),
                getClass().getClassLoader().getResource("noagain.xml"));
    }
}
