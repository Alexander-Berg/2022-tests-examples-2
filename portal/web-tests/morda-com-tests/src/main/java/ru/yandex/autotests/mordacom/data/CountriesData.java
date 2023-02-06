package ru.yandex.autotests.mordacom.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.language.Language;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.startsWith;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.WORLDWIDE_TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.WORLDWIDE_RU;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.WORLDWIDE_BE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.WORLDWIDE_UK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.WORLDWIDE_KK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.WORLDWIDE_TR;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: leonsabr
 * Date: 18.08.2010
 */
public class CountriesData {

    private static final Properties CONFIG = new Properties();

    private static final String HTTP_WWW_YANDEX_RU = CONFIG.getProtocol() + "://www.yandex.ru/";
    private static final String YANDEX_RU_IMG = CONFIG.getProtocol() + "://yastatic.net/lego/_/Spb22l3caaD3xN3g-_nuzdnS2FA.png";

    private static final String HTTP_WWW_YANDEX_BY = CONFIG.getProtocol() + "://www.yandex.by/";
    private static final String YANDEX_BY_IMG = CONFIG.getProtocol() + "://yastatic.net/lego/_/O-tmndNZfQ0UH_3x69kKVSzOLpY.png";

    private static final String HTTP_WWW_YANDEX_UA = CONFIG.getProtocol() + "://www.yandex.ua/";
    private static final String YANDEX_UA_IMG = CONFIG.getProtocol() + "://yastatic.net/lego/_/QaG3XxXylZ5KP1AZC_bZ0nO3u5M.png";

    private static final String HTTP_WWW_YANDEX_KZ = CONFIG.getProtocol() + "://www.yandex.kz/";
    private static final String YANDEX_KZ_IMG = CONFIG.getProtocol() + "://yastatic.net/lego/_/uzZ71PWcVXtsIkeTuwAakheaPOY.png";

    private static final String HTTP_WWW_YANDEX_COM_TR = CONFIG.getProtocol() + "://www.yandex.com.tr/";
    private static final String YANDEX_COM_TR_IMG = CONFIG.getProtocol() + "://yastatic.net/lego/_/WEqF7-mdxlQe_LncWQpTHfzqEeE.png";

    public static List<CountryInfo> getCountriesList(Language language) {
        List<CountryInfo> countries = new ArrayList<>();
        countries.add(new CountryInfo(
                WORLDWIDE_RU, language,
                startsWith(HTTP_WWW_YANDEX_RU),
                equalTo(YANDEX_RU_IMG)
        ));
        countries.add(new CountryInfo(
                WORLDWIDE_BE, language,
                startsWith(HTTP_WWW_YANDEX_BY),
                equalTo(YANDEX_BY_IMG)
        ));
        countries.add(new CountryInfo(
                WORLDWIDE_UK, language,
                startsWith(HTTP_WWW_YANDEX_UA),
                equalTo(YANDEX_UA_IMG)
        ));
        countries.add(new CountryInfo(
                WORLDWIDE_KK, language,
                startsWith(HTTP_WWW_YANDEX_KZ),
                equalTo(YANDEX_KZ_IMG)
        ));
        countries.add(new CountryInfo(
                WORLDWIDE_TR, language,
                startsWith(HTTP_WWW_YANDEX_COM_TR),
                equalTo(YANDEX_COM_TR_IMG)
        ));
        return countries;
    }



    public static Matcher<String> getTextYandexInMatcher(Language language) {
        return equalTo(getTranslation(WORLDWIDE_TITLE, language));
    }

    public static class CountryInfo extends LinkInfo {
        public Matcher<String> img;

        public CountryInfo(TextID textID, Language language, Matcher<String> url, Matcher<String> img) {
            super(equalTo(getTranslation(textID, language)), url);
            this.img = img;
        }

        @Override
        public String toString() {
            return text.toString();
        }
    }
}
