package ru.yandex.autotests.dictionary;

import org.junit.Test;
import ru.yandex.autotests.dictionary.cleaners.HomeCleaner;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.Assert.assertThat;

/**
 * User: leonsabr
 * Date: 01.11.11
 */
public class HomeCleanerTest {
    @Test
    public void cleanerOff() {
        Tanker tanker = new Tanker(getClass().getClassLoader().getResource("home.xml"));
        assertThat(tanker.get("home", "allServices", "personalBlock.mail.desc", "ru"), equalTo("Без спама, вирусов и&#160;рекламы"));
        assertThat(tanker.get(new TextID("home", "fotki", "photoTitleK"), "tt"), equalTo("Бүгенге фотога<br>&#32;кандидат"));
    }

    @Test
    public void cleanerOn() {
        Tanker tanker = new Tanker(new HomeCleaner(), getClass().getClassLoader().getResource("home.xml"));
        assertThat(tanker.get("home", "allServices", "personalBlock.mail.desc", "ru"), equalTo("Без спама, вирусов и рекламы"));
        assertThat(tanker.get(new TextID("home", "fotki", "photoTitleK"), "tt"), equalTo("Бүгенге фотога\n кандидат"));
    }
}
