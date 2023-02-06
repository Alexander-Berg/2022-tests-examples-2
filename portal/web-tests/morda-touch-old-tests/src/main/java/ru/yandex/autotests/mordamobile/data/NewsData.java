package ru.yandex.autotests.mordamobile.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.Properties;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.LanguageMatcher.inLanguage;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.NEWS_AUTO;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.NEWS_BUSINESS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.NEWS_CULTURE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.NEWS_INCIDENT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.NEWS_MAIN;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.NEWS_POLITICS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.NEWS_SCIENCE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.NEWS_SELECT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.NEWS_SOCIETY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.NEWS_SPORT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.NEWS_TODAY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.NEWS_WORLD;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.NEWS_COMPUTERS;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class NewsData {
    private static final Properties CONFIG = new Properties();

    public static final LinkInfo TITLE_LINK = new LinkInfo(
            equalTo(getTranslation(NEWS_TODAY, CONFIG.getLang())),
            startsWith("https://m.news.yandex" + CONFIG.getBaseDomain() + "/")
    );

    private static final String NEWS_URL_PATTERN = "http://m.news.yandex%s/yandsearch?cl4url=";
    private static final String NEWS_HTTPS_URL_PATTERN = "https://m.news.yandex%s/yandsearch?cl4url=";
    private static final String BLOGS_URL_PATTERN = "http://m.blogs.yandex%s/search.xml?";

    public static final LinkInfo NEWS_LINK = new LinkInfo(
            inLanguage(CONFIG.getLang()),
            startsWith(String.format(NEWS_HTTPS_URL_PATTERN, CONFIG.getBaseDomain())),
            hasAttribute(HREF, startsWith(String.format(NEWS_HTTPS_URL_PATTERN, CONFIG.getBaseDomain())))
    );

    public static final LinkInfo BLOGS_LINK = new LinkInfo(
            inLanguage(CONFIG.getLang()),
            startsWith(String.format(BLOGS_URL_PATTERN, CONFIG.getBaseDomain()))
    );

    public static final Matcher<String> SELECT_BUTTON_TEXT = equalTo(getTranslation(NEWS_SELECT, CONFIG.getLang()));

    public static enum Category {
        MAIN(NEWS_MAIN, "https://m.news.yandex%s/index", NEWS_LINK),
        POLITICS(NEWS_POLITICS, "https://m.news.yandex%s/politics.html", NEWS_LINK),
        WORLD(NEWS_WORLD, "https://m.news.yandex%s/world.html", NEWS_LINK),
        SOCIETY(NEWS_SOCIETY, "https://m.news.yandex%s/society.html", NEWS_LINK),
        BUSINESS(NEWS_BUSINESS, "https://m.news.yandex%s/business.html", NEWS_LINK),
        SPORT(NEWS_SPORT, "https://m.news.yandex%s/sport.html", NEWS_LINK),
        INCIDENT(NEWS_INCIDENT, "https://m.news.yandex%s/incident.html", NEWS_LINK),
        CULTURE(NEWS_CULTURE, "https://m.news.yandex%s/culture.html", NEWS_LINK),
        SCIENCE(NEWS_SCIENCE, "https://m.news.yandex%s/science.html", NEWS_LINK),
        COMPUTERS(NEWS_COMPUTERS, "https://m.news.yandex%s/computers.html", NEWS_LINK),
        AUTO(NEWS_AUTO, "https://m.news.yandex%s/auto.html", NEWS_LINK);

        private Category(TextID name, String urlPattern, LinkInfo searchLink) {
            this.name = equalTo(getTranslation(name, CONFIG.getLang()));

            this.url = startsWith(String.format(urlPattern, CONFIG.getBaseDomain()));

            this.searchLink = searchLink;
        }

        private Category(Matcher<String> name, Matcher<String> url) {
            this.name = name;
            this.url = url;
        }

        private Matcher<String> name;
        private Matcher<String> url;
        private LinkInfo searchLink;

        public Matcher<String> getName() {
            return name;
        }

        public Matcher<String> getUrl() {
            return url;
        }

        public LinkInfo getSearchLink() {
            return searchLink;
        }
    }

}
