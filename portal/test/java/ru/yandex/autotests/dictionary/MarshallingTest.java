package ru.yandex.autotests.dictionary;

import org.junit.Test;
import ru.yandex.autotests.dictionary.cleaners.HomeCleaner;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.Assert.assertThat;

/**
 * User: leonsabr
 * Date: 25.10.11
 */
public class MarshallingTest {
    @Test
    public void loadFromXmlHome() {
        Tanker tanker = new Tanker(new HomeCleaner(), getClass().getClassLoader().getResource("home.xml"));
        assertThat(tanker.get(new TextID("home", "afisha", "cards"), "ru"), equalTo("Новогодние открытки"));
        assertThat(tanker.get("home", "allServices", "apiBlock.api_blogs.title", "uk"), equalTo("Пошук у блогах"));
        assertThat(tanker.get(new TextID("home", "allskins", "beach"), "kk"), equalTo("жағажай"));
        assertThat(tanker.get(new TextID("home", "blogs", "pulse"), "tt"), equalTo("Язның йөрәк тибеше"));
        assertThat(tanker.get("home", "catalog", "returnToCatalog", "be"), equalTo("Вярнуцца ў каталог"));
        assertThat(tanker.get(new TextID("home", "disaster", "none"), "tr"), equalTo("Ölü veya yaralı yok"));
        assertThat(tanker.get(new TextID("home", "domik", "loginfrom"), "en"), equalTo("username from..."));

        assertThat(tanker.get(new TextID("home", "mail", "num.file", Plural.ONE), "ru"), equalTo("файл"));
        assertThat(tanker.get("home", "traffic", "personal.rate", Plural.SOME, "be"), equalTo("балы"));
        assertThat(tanker.get("home", "search_teaser", "product_offers", Plural.MANY, "uk"), equalTo("пропозицій"));
        assertThat(tanker.get(new TextID("home", "mail", "num.new_messages", Plural.NONE), "tr"), equalTo("yeni e-posta"));
    }

    @Test
    public void loadFromXmlSerp() {
        Tanker tanker = new Tanker(new HomeCleaner(), getClass().getClassLoader().getResource("serp.xml"));
        assertThat(tanker.get(new TextID("serp", "serp-news",
                "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>[Председатель правления] [нефтяной компании] [ЮКОС] [Михаил Ходорковский]"), "ru"),
                equalTo("      [Председатель правления] [нефтяной компании] [ЮКОС] [Михаил Ходорковский]"));
    }
}
