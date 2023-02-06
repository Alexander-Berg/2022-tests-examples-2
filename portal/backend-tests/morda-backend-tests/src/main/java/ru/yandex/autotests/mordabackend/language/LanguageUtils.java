package ru.yandex.autotests.mordabackend.language;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordabackend.MordaClient.getJsonEnabledClient;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.getRegionParents;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TR;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.ADANA;
import static ru.yandex.autotests.utils.morda.region.Region.ALANYA;
import static ru.yandex.autotests.utils.morda.region.Region.ALMATY;
import static ru.yandex.autotests.utils.morda.region.Region.ANTALYA;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.BURSA;
import static ru.yandex.autotests.utils.morda.region.Region.CHELYABINSK;
import static ru.yandex.autotests.utils.morda.region.Region.DNEPROPETROVSK;
import static ru.yandex.autotests.utils.morda.region.Region.DUBNA;
import static ru.yandex.autotests.utils.morda.region.Region.EKATERINBURG;
import static ru.yandex.autotests.utils.morda.region.Region.GAZIANTEP;
import static ru.yandex.autotests.utils.morda.region.Region.HARKOV;
import static ru.yandex.autotests.utils.morda.region.Region.ISTANBUL;
import static ru.yandex.autotests.utils.morda.region.Region.IZMIR;
import static ru.yandex.autotests.utils.morda.region.Region.KAZAN;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MERSIN;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.NOVOSIBIRSK;
import static ru.yandex.autotests.utils.morda.region.Region.PERM;
import static ru.yandex.autotests.utils.morda.region.Region.SAMARA;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;
import static ru.yandex.autotests.utils.morda.region.Region.TATARSTAN;
import static ru.yandex.autotests.utils.morda.region.Region.UFA;
import static ru.yandex.autotests.utils.morda.region.Region.UKRAINE;
import static ru.yandex.autotests.utils.morda.region.Region.VLADIVOSTOK;
import static ru.yandex.autotests.utils.morda.region.Region.YAROSLAVL;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29.07.14
 */
public class LanguageUtils {

    private static final String LANG_HREF_PATTERN = "%s/?lang=%s&sk=%s";

    public static final List<Region> LANGUAGE_REGIONS_MAIN = Arrays.asList(
            MOSCOW, KIEV, SANKT_PETERBURG, MINSK, EKATERINBURG, PERM,
            SAMARA, CHELYABINSK, NOVOSIBIRSK, DUBNA, ASTANA, ALMATY,
            VLADIVOSTOK, UFA, YAROSLAVL, HARKOV, DNEPROPETROVSK, KAZAN
    );

    public static final List<Region> LANGUAGE_REGIONS_TR = Arrays.asList(
            ISTANBUL, BURSA, ALANYA, ANTALYA, IZMIR, ADANA, GAZIANTEP, MERSIN
    );

    public static final List<Region> LANGUAGE_REGIONS_ALL = new ArrayList<>();
    static {
        LANGUAGE_REGIONS_ALL.addAll(LANGUAGE_REGIONS_MAIN);
        LANGUAGE_REGIONS_ALL.addAll(LANGUAGE_REGIONS_TR);
    }

    private static final Map<Domain, Language> DOMAIN_LANGUAGE_MAP = new HashMap<>();
    static {
        DOMAIN_LANGUAGE_MAP.put(Domain.RU, RU);
        DOMAIN_LANGUAGE_MAP.put(Domain.UA, UK);
        DOMAIN_LANGUAGE_MAP.put(Domain.BY, BE);
        DOMAIN_LANGUAGE_MAP.put(Domain.KZ, KK);
        DOMAIN_LANGUAGE_MAP.put(COM_TR, TR);
    }

    public static Matcher<String> getLangMatcher(String locale) {
        return equalTo(Language.getLanguage(locale).getValue());
    }

    public static Matcher<String> getLangHrefMatcher(String host, String locale, String sk) {
        return equalTo(String.format(LANG_HREF_PATTERN, host, locale, sk));
    }

    public static Language getDefaultLanguage(Region region, UserAgent userAgent) {
        if (region.getDomain().equals(COM_TR)) {
            return TR;
        }
        if ( getRegionParents(getJsonEnabledClient(), region.getRegionIdInt()).contains(UKRAINE.getRegionIdInt())) {
            return UK;
        }
        return RU;
    }

    public static Language getNationalLanguage(Region region) {
        if (getRegionParents(getJsonEnabledClient(), region.getRegionIdInt()).contains(TATARSTAN.getRegionIdInt())) {
            return TT;
        }
        return DOMAIN_LANGUAGE_MAP.get(region.getDomain());
    }

    public static List<Language> getDefaultRegionLanguages(Region region) {
        if (getRegionParents(getJsonEnabledClient(), region.getRegionIdInt()).contains(Region.ROSSIYA.getRegionIdInt()) &&
                !getRegionParents(getJsonEnabledClient(), region.getRegionIdInt()).contains(Region.TATARSTAN.getRegionIdInt())
                || region.getDomain().equals(COM_TR)) {
            return new ArrayList<>();
        }
        return new ArrayList<>(Arrays.asList(getNationalLanguage(region), RU));
    }

    public static Collection<Language> getRegionLanguages(Region region, Language currentLanguage) {
        if (getRegionParents(getJsonEnabledClient(), region.getRegionIdInt()).contains(Region.ROSSIYA.getRegionIdInt()) &&
                !getRegionParents(getJsonEnabledClient(), region.getRegionIdInt()).contains(Region.TATARSTAN.getRegionIdInt()) &&
                currentLanguage.equals(RU)) {
            return new ArrayList<>();
        }
        Set<Language> defaultLanguages = new HashSet<>(Arrays.asList(getNationalLanguage(region), RU));
        defaultLanguages.add(currentLanguage);
        return defaultLanguages;
    }

    public static Language getSelectedLanguage(Region region, Language currentLanguage) {
        if (getRegionParents(getJsonEnabledClient(), region.getRegionIdInt()).contains(Region.ROSSIYA.getRegionIdInt()) &&
                !getRegionParents(getJsonEnabledClient(), region.getRegionIdInt()).contains(Region.TATARSTAN.getRegionIdInt()) &&
                currentLanguage.equals(RU)) {
            return null;
        }
        return currentLanguage;
    }
}
