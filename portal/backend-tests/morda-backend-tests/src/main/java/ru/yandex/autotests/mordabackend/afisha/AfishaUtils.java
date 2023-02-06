package ru.yandex.autotests.mordabackend.afisha;

import ch.lambdaj.Lambda;
import org.hamcrest.Matcher;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaEvent;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaPosters;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaPremiereEvent;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.region.RegionManager;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.lang.String.format;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.lessThanOrEqualTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.morda.utils.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordacommonsteps.matchers.LanguageMatcher.inLanguage;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_V12_2;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.ServicesV122EntryMatcher.with;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Afisha.PREMIERE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Afisha.PREMIERE_IN;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.AFTERTOMORROW;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.TOMORROW;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.Region.ADANA;
import static ru.yandex.autotests.utils.morda.region.Region.ANKARA;
import static ru.yandex.autotests.utils.morda.region.Region.ANTALYA;
import static ru.yandex.autotests.utils.morda.region.Region.BURSA;
import static ru.yandex.autotests.utils.morda.region.Region.CHEBOKSARI;
import static ru.yandex.autotests.utils.morda.region.Region.CHELYABINSK;
import static ru.yandex.autotests.utils.morda.region.Region.DNEPROPETROVSK;
import static ru.yandex.autotests.utils.morda.region.Region.DUBNA;
import static ru.yandex.autotests.utils.morda.region.Region.EKATERINBURG;
import static ru.yandex.autotests.utils.morda.region.Region.HABAROVSK;
import static ru.yandex.autotests.utils.morda.region.Region.HARKOV;
import static ru.yandex.autotests.utils.morda.region.Region.IRKUTSK;
import static ru.yandex.autotests.utils.morda.region.Region.ISTANBUL;
import static ru.yandex.autotests.utils.morda.region.Region.IZMIR;
import static ru.yandex.autotests.utils.morda.region.Region.KALININGRAD;
import static ru.yandex.autotests.utils.morda.region.Region.KAZAN;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.KRASNODAR;
import static ru.yandex.autotests.utils.morda.region.Region.KRASNOYARSK;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.MURMANSK;
import static ru.yandex.autotests.utils.morda.region.Region.NIZHNIY_NOVGOROD;
import static ru.yandex.autotests.utils.morda.region.Region.NOVOSIBIRSK;
import static ru.yandex.autotests.utils.morda.region.Region.PERM;
import static ru.yandex.autotests.utils.morda.region.Region.PETROZAVODSK;
import static ru.yandex.autotests.utils.morda.region.Region.ROSTOV_NA_DONU;
import static ru.yandex.autotests.utils.morda.region.Region.SAMARA;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;
import static ru.yandex.autotests.utils.morda.region.Region.SEVASTOPOL;
import static ru.yandex.autotests.utils.morda.region.Region.SIMFEROPOL;
import static ru.yandex.autotests.utils.morda.region.Region.TOMSK;
import static ru.yandex.autotests.utils.morda.region.Region.TULA;
import static ru.yandex.autotests.utils.morda.region.Region.UFA;
import static ru.yandex.autotests.utils.morda.region.Region.VLADIVOSTOK;
import static ru.yandex.autotests.utils.morda.region.Region.VOLGOGRAD;
import static ru.yandex.autotests.utils.morda.region.Region.VORONEZH;
import static ru.yandex.autotests.utils.morda.region.Region.YAROSLAVL;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: ivannik
 * Date: 30.06.2014
 */
public class AfishaUtils {

    public static final List<Language> LANGUAGES = Arrays.asList(RU, UK, BE, KK, TT);

    public static final List<Region> AFISHA_REGIONS_MAIN = Arrays.asList(
            CHEBOKSARI, CHELYABINSK, DNEPROPETROVSK, EKATERINBURG,
            HABAROVSK, IRKUTSK, HARKOV, KALININGRAD, KRASNODAR, KRASNOYARSK, KIEV, KAZAN,
            MINSK, MURMANSK, MOSCOW, NIZHNIY_NOVGOROD, NOVOSIBIRSK, PERM, PETROZAVODSK,
            ROSTOV_NA_DONU, SEVASTOPOL, SIMFEROPOL, SAMARA, SANKT_PETERBURG, TOMSK,
            TULA, UFA, VLADIVOSTOK, VOLGOGRAD, VORONEZH, YAROSLAVL, DUBNA
    );


    public static final List<Region> AFISHA_REGIONS_TR = Arrays.asList(
            ISTANBUL, ADANA, ANKARA, BURSA, IZMIR, ANTALYA
    );

    public static final List<Region> AFISHA_REGIONS_ALL = new ArrayList<>();
    public static final Map<Region, Region> REGION_REMAP = new HashMap<Region, Region>() {{
        put(DUBNA, MOSCOW);
    }};
    public static final Matcher<String> POSTER_BASE_URL_MATCHER =
            matches("https://avatars.mds.yandex.net/get-afishanew/\\d{5}/[\\da-f]{32}/");

    static {
        AFISHA_REGIONS_ALL.addAll(AFISHA_REGIONS_MAIN);
    }

    public static String getAfishaHref(UserAgent userAgent, Region region) {
        if (userAgent.getIsTouch() == 1) {
            return format("https://afisha.yandex%s", region.getDomain());
        }
        if (userAgent.isMobile()) {
            return export(SERVICES_V12_2, domain(region.getDomain()), with().id("afisha")).getPda()
                    .replaceAll("http:", "https:");
        }
        return export(SERVICES_V12_2, domain(region.getDomain()), with().id("afisha")).getHref();
    }

    public static Matcher<Collection<?>> getPremiereSize() {
        return hasSize(lessThanOrEqualTo(4));
    }

    public static Matcher<Collection<?>> getPremiereGenreSize(Region region) {
//        if (isDayIn(region, THURSDAY, FRIDAY, SATURDAY, SUNDAY)) {
//            return Matchers.allOf(hasSize(greaterThan(0)), hasSize(lessThanOrEqualTo(3)));
//        } else {
            return hasSize(lessThanOrEqualTo(5));
//        }
    }

    public static String getPremiereMessage(Language lang) {
        return getTranslation(PREMIERE, lang);
    }

    public static String getPremiereTomorrowMessage(Language lang) {
        return getTranslation(PREMIERE_IN, lang) + " " + getTranslation(TOMORROW, lang);
    }

    public static String getPremiereAfterTomorrowMessage(Language lang) {
        return getTranslation(PREMIERE_IN, lang) + " " + getTranslation(AFTERTOMORROW, lang);
    }

    public static Matcher<AfishaPremiereEvent> getNoPremiereMatcher(String premiereMessage) {
        return not(Lambda.<AfishaPremiereEvent, String>having(
                        on(AfishaPremiereEvent.class).getPremday(), equalTo(premiereMessage))
        );
    }

    public static boolean isDayIn(Region region, int... daysOfWeek) {
        int currentDay = getAfishaDayOfWeek(region);
        for (int dayOfWeek : daysOfWeek) {
            if (dayOfWeek == currentDay) {
                return true;
            }
        }
        return false;
    }

    public static int getAfishaDayOfWeek(Region region) {
        Calendar c = Calendar.getInstance(region.getTimezone());
        c.add(Calendar.HOUR_OF_DAY, -6);
        return c.get(Calendar.DAY_OF_WEEK);
    }

    public static int getExpectedNumberOfAfishaEvents(Region region) {
        if (region.getDomain().equals(COM_TR)) {
            return 3;
        }
        return isMiddleOfWeek(RegionManager.getDayOfWeek(region)) ? 3 : 5;
    }

    private static boolean isMiddleOfWeek(int day) {
        return day >= 2 && day <= 4;
    }

    @Step("Should have event {0}")
    public static void shouldHaveEvent(String eventName, AfishaEvent event, Language language,
                                       int eventCount, UserAgent userAgent) {
        int baseMaxNameLength = 25;
        shouldHaveParameter(event, having(on(AfishaEvent.class).getName(), not(equalTo(""))));
        shouldHaveParameter(event, having(on(AfishaEvent.class).getName(), inLanguage(language)));
        shouldHaveParameter(event, having(on(AfishaEvent.class).getFull(), inLanguage(language)));

        int maxNameLength = (eventCount > 3 && !userAgent.isMobile()) ? baseMaxNameLength : baseMaxNameLength * 2;
        int nameLength;
        if (event.getFull().length() > maxNameLength) {
            nameLength = event.getFull().substring(0, maxNameLength + 1).lastIndexOf(' ');
            if (nameLength < 0) {
                nameLength = event.getFull().indexOf(' ', maxNameLength);
            }
            if (nameLength < 0) {
                nameLength = event.getFull().length();
            }
            if (!event.getFull().substring(0, nameLength).endsWith(".") &&
                    !event.getFull().substring(0, nameLength).endsWith(":")) {
                ++nameLength;
            }
        } else {
            nameLength = event.getFull().length();
        }

        assertThat("Name length greater than " + nameLength + ": " + event,
                event.getName().length(), equalTo(nameLength));
        if (event.getFull().length() > maxNameLength) {
            assertThat("Title length less or equal than " + maxNameLength + ": " + event,
                    event.getTitle().length(), greaterThan(maxNameLength));
            assertThat("Full length less or equal than " + maxNameLength + ": " + event,
                    event.getFull().length(), greaterThan(maxNameLength));
            shouldHaveParameter(event, having(on(AfishaEvent.class).getTitle(), inLanguage(language)));
            shouldHaveParameter(event, having(on(AfishaEvent.class).getFull(),
                    startsWith(event.getName().substring(0, event.getName().length() - 1))));
        } else {
            shouldHaveParameter(event, having(on(AfishaEvent.class).getFull(), equalTo(event.getName().trim())));
            assertThat("Full length greater than " + maxNameLength + ": " + event,
                    event.getFull().length(), lessThanOrEqualTo(maxNameLength));
        }
    }

    @Step("Should have event posters {0}")
    public static void shouldHaveEventPosters(String eventName, AfishaEvent event, Client client, UserAgent userAgent)
            throws IOException {

        shouldMatchTo(event.getPosters(),
                hasPropertyWithValue(on(AfishaPosters.class).getBase(), POSTER_BASE_URL_MATCHER)
        );
        shouldHaveResponseCode(client, normalizeUrl(event.getPosters().getBase() + "100x143_noncrop"), userAgent, equalTo(200));
    }

    @Step("Should have event link {0}")
    public static void shouldHaveEventLink(String eventName, AfishaEvent event, Client client,
                                           UserAgent userAgent, String afishaHref)
            throws IOException {
        shouldHaveParameter(normalizeUrl(event.getHref()), startsWith(afishaHref));
        shouldHaveParameter(normalizeUrl(event.getRawHref()), startsWith(afishaHref));
        shouldHaveResponseCode(client, normalizeUrl(event.getRawHref()), userAgent, equalTo(200));
    }
}
