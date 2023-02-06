package ru.yandex.autotests.dictionary;

import org.junit.Test;
import ru.yandex.autotests.dictionary.cleaners.HomeCleaner;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.Assert.assertThat;

/**
 * User: leonsabr
 * Date: 22.11.11
 */
public class AdditionalExportsTest {
    @Test
    public void tankerLocalCleaner() {
        Tanker tanker = new Tanker(new HomeCleaner(),
                getClass().getClassLoader().getResource("home.xml"),
                getClass().getClassLoader().getResource("serp.xml"),
                getClass().getClassLoader().getResource("local.xml"));

        assertThat(tanker.get("home", "allServices", "personalBlock.mail.desc", "ru"), equalTo("Без спама, вирусов и рекламы"));
        assertThat(tanker.get("local", "traffic", "points.6", "tr"), equalTo("Çok yoğun trafik"));
        assertThat(tanker.get("serp", "serp-news",
                "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>[Председатель правления] [нефтяной компании] [ЮКОС] [Михаил Ходорковский]", "ru"),
                equalTo("      [Председатель правления] [нефтяной компании] [ЮКОС] [Михаил Ходорковский]"));
    }
}
