package ru.yandex.autotests.widgets.data;


import org.hamcrest.Matcher;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.language.Language;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_ADV;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_AUTO;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_BUSINESS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_CULTURE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_EDUCATION;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_ENTERTAINMENT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_GAMES;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_HOME;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_INFO;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_JOB;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_NEWS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_SPORT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_TECHNOLOGY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_TOURISM;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.RUBRIC_YANDEX;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: leonsabr
 * Date: 08.11.11
 */
public class SearchData {
    public static enum Category {
        AUTO(RUBRIC_AUTO, "/rubric/cars/"),
        BUSINESS(RUBRIC_BUSINESS, "/rubric/business/"),
        HOME(RUBRIC_HOME, "/rubric/home/"),
        GAMES(RUBRIC_GAMES, "/rubric/games/"),
        CULTURE(RUBRIC_CULTURE, "/rubric/culture/"),
        NEWS(RUBRIC_NEWS, "/rubric/news/"),
        EDUCATION(RUBRIC_EDUCATION, "/rubric/education/"),
        ADV(RUBRIC_ADV, "/rubric/advertisement/"),
        JOB(RUBRIC_JOB, "/rubric/job/"),
        ENTERTAINMENT(RUBRIC_ENTERTAINMENT, "/rubric/entertainment/"),
        SPORT(RUBRIC_SPORT, "/rubric/sport/"),
        INFO(RUBRIC_INFO, "/rubric/information/"),
        TECHNOLOGY(RUBRIC_TECHNOLOGY, "/rubric/technology/"),
        TOURISM(RUBRIC_TOURISM, "/rubric/tourism/"),
        YANDEX(RUBRIC_YANDEX, "/?company=yandex");

        private TextID text;
        private String url;

        private Category(TextID text, String url) {
            this.text = text;
            this.url = url;
        }

        public Matcher<String> getText(Language lang) {
            return equalTo(getTranslation(text, lang));
        }

        public void setText(TextID text) {
            this.text = text;
        }

        public String getUrl(String host) {
            return host + url;
        }

        public void setUrl(String url) {
            this.url = url;
        }

        public LinkInfo getLink(String host, Language lang) {
            return new LinkInfo(
                    getText(lang),
                    equalTo(host + url)
            );
        }
    }

    public static final Matcher<String> WIDGETS_NUMBER_MATCHER = matches("[0-9]+ .*");

    public static final Map<String, List<String>> REQUESTS = new HashMap<String, List<String>>() {
        private void put(String req, String... resps) {
            put(req, asList(resps));
        }

        {
            put("псков", "псков");
            put("свежие", "свеж");
            put("kaz", "kaz");
            put("мода", "мод");
            put("комсомольская правда", "комсомол");
            put("kp.ru", "комсомольская правда");
            put("максимум", "максимум");
            put("Спорт новости", "спорт");
            put("apple", "apple");
            put("интернет-магазин", "интернет-магазин");
            put("internet", "internet");
            put("mail", "mail");
            put("кошка", "кошка");
            put("афоризм", "афоризм");
            put("спортивные новости", "новост");
            put("Университет", "университет");
            put("праздники", "праздник");
            put("отдам даром", "отдам даром");
            put("vk.com", "вконтакте");
            put("авто", "авто");
            put("4PDA.RU", "4PDA.RU");
            put("lenta.ru", "lenta.ru");
            put("google.com");
            put("Погода", "погода");
            put("погода", "погода");
            put("погод", "погода");
            put("google", "google");
            put("омск", "омск");
            put("Омск", "омск");
            put("omsk", "омск");
            put("Omsk", "омск");
            put("yandex", "yandex.ru");
            put("yandex.ru", "yandex.ru");
            put("job", "ваканси");
            put("вакансии", "ваканси");
            put("казахстан", "казахстан");
            put("Казахстан", "казахстан");
            put("kz", "kz");
            put("KZ", "kz");
            put("Россия", "росси");
            put("pоссия", "росси");
            put("календарь", "календ");
            put("Календарь", "календ");
            put("petersburg", "петербург");
            put("Петербург", "петербург");
            put("Санкт-Петербург", "петербург");
            put("Санкт Петербург", "петербург");
            put("zenit", "зенит");
            put("ФК Зенит", "зенит");
            put("Погода в Москве");
            put("вакыйгалар тасмасын күрсәтү", "вакыйгалар", "тасмасын", "күрсәтү");
            put("работа в Беларуси", "работа", "вакансии", "белорус");
        }
    };

    public static final Map<String, String> URL_REQUESTS = new HashMap<String, String>() {{
        put("lenta.ru", "lenta.ru");
        put("sports.ru", "sports.ru");
        put("news.yandex.ru", "news.yandex.ru");
        put("4pda.ru", "4pda.ru");
        put("sports.ru%2Ffootball%2F&from=yaca", "sports.ru");
        put("sports.ru%2Fhockey%2F&from=yaca", "sports.ru");
    }};
}
