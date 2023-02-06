package ru.yandex.autotests.mordamobile.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.Properties;

import java.util.Arrays;
import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.LanguageMatcher.inLanguage;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Afisha.TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class AfishaData {
    private static final Properties CONFIG = new Properties();

    private static final Matcher<String> AFISHA_HREF_MATCHER =
            matches("https://afisha\\.yandex\\.ru/events/[\\da-а]{24}\\?city=\\w+&version=mobile");

    public static final LinkInfo TITLE_LINK = new LinkInfo(
            equalTo(getTranslation(TITLE, CONFIG.getLang())),
            matches("https://afisha\\.yandex\\.ru/\\?city=\\w+&version=mobile")
    );

    public static final LinkInfo AFISHA_LINK = new LinkInfo(
            inLanguage(CONFIG.getLang()),
            AFISHA_HREF_MATCHER
    );

    public static final List<String> GENRES = Arrays.asList(
            "детектив",
            "биографический",
            "боевик",
            "приключения",
            "комедия",
            "драма",
            "премьера",
            "триллер",
            "ужасы",
            "экшн",
            "экшен",
            "кино",
            "анимационная комедия",
            "криминал",
            "военный",
            "спорт",
            "фантастика",
            "фэнтези",
            "экшн-комедия",
            "мультфильм",
            "анимация",
            "кинофестиваль",
            "мюзикл",
            "мелодрама",
            "музыкальный",
            "исторический",
            "короткометражный фильм",
            "комедийный боевик",
            "анимационный",
            "приключенческий боевик",
            "семейный",
            "мистика"
    );
}
