package ru.yandex.autotests.dictionary;

import org.junit.Test;
import ru.yandex.autotests.dictionary.cleaners.HomeCleaner;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.Assert.assertThat;

/**
 * User: leonsabr
 * Date: 21.11.11
 */
public class LocalDictionaryTest {
    @Test
    public void tankerLocalCleaner() {
        Tanker tanker = new Tanker(new HomeCleaner(), getClass().getClassLoader().getResource("home.xml"),
                getClass().getClassLoader().getResource("local.xml"));
        assertThat(tanker.get("home", "allServices", "personalBlock.mail.desc", "ru"), equalTo("Без спама, вирусов и рекламы"));
        assertThat(tanker.get(new TextID("home", "fotki", "photoTitleK"), "tt"), equalTo("Бүгенге фотога\n кандидат"));
        assertThat(tanker.get("local", "traffic", "points.6", "tr"), equalTo("Çok yoğun trafik"));
    }

    @Test
    public void tankerLocal() {
        Tanker tanker = new Tanker(getClass().getClassLoader().getResource("home.xml"),
                getClass().getClassLoader().getResource("local.xml"));
        assertThat(tanker.get("home", "allServices", "personalBlock.mail.desc", "ru"), equalTo("Без спама, вирусов и&#160;рекламы"));
        assertThat(tanker.get(new TextID("home", "fotki", "photoTitleK"), "tt"), equalTo("Бүгенге фотога<br>&#32;кандидат"));
        assertThat(tanker.get("local", "traffic", "points.1", "ru"), equalTo("На дорогах свободно"));
    }

    @Test
    public void localCleaner() {
        Tanker tanker = new Tanker(new HomeCleaner(), getClass().getClassLoader().getResource("local.xml"));
        assertThat(tanker.get("local", "traffic", "points.7", "tt"), equalTo("Авыр тыгынлыклар"));
        assertThat(tanker.get("local", "traffic", "points.2", "be"), equalTo("Дарогі амаль свабодныя"));
    }

    @Test
    public void local() {
        Tanker tanker = new Tanker(getClass().getClassLoader().getResource("local.xml"));
        assertThat(tanker.get("local", "traffic", "points.10", "uk"), equalTo("Краще їхати на метро"));
        assertThat(tanker.get("local", "traffic", "points.5", "kk"), equalTo("Тығыз қозғалыс"));
    }
}
