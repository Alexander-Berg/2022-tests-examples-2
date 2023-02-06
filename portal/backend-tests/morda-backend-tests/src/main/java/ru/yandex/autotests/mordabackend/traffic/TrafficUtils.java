package ru.yandex.autotests.mordabackend.traffic;

import org.hamcrest.Matcher;
import org.joda.time.Interval;
import org.joda.time.LocalDateTime;
import org.joda.time.LocalTime;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.traffic.Future;
import ru.yandex.autotests.mordabackend.beans.traffic.Informer;
import ru.yandex.autotests.mordabackend.beans.traffic.Traffic;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordaexportsclient.MordaExports;
import ru.yandex.autotests.mordaexportsclient.beans.TrafinfoEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.lessThanOrEqualTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.nullValue;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.Region.ANKARA;
import static ru.yandex.autotests.utils.morda.region.Region.BURSA;
import static ru.yandex.autotests.utils.morda.region.Region.CHELYABINSK;
import static ru.yandex.autotests.utils.morda.region.Region.EKATERINBURG;
import static ru.yandex.autotests.utils.morda.region.Region.ISTANBUL;
import static ru.yandex.autotests.utils.morda.region.Region.IZMIR;
import static ru.yandex.autotests.utils.morda.region.Region.KAZAN;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.LYUDINOVO;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.NIZHNIY_NOVGOROD;
import static ru.yandex.autotests.utils.morda.region.Region.NOVOSIBIRSK;
import static ru.yandex.autotests.utils.morda.region.Region.PERM;
import static ru.yandex.autotests.utils.morda.region.Region.ROSTOV_NA_DONU;
import static ru.yandex.autotests.utils.morda.region.Region.SAMARA;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;
import static ru.yandex.autotests.utils.morda.region.Region.VOLGOGRAD;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: ivannik
 * Date: 23.07.2014
 */
public class TrafficUtils {

    public static final List<Language> LANGUAGES = Arrays.asList(RU, UK, BE, KK);
    public static final List<Region> TRAFFIC_REGIONS_MAIN = Arrays.asList(MOSCOW, KIEV, SANKT_PETERBURG, EKATERINBURG, PERM,
            SAMARA, CHELYABINSK, NOVOSIBIRSK, KAZAN, NIZHNIY_NOVGOROD, VOLGOGRAD, ROSTOV_NA_DONU, LYUDINOVO);

    public static final List<Region> TRAFFIC_REGIONS_TR = Arrays.asList(
            ISTANBUL,
            IZMIR,
            BURSA,
            ANKARA
    );

    public static final List<Region> TRAFFIC_REGIONS_ALL = new ArrayList<>();
    public static final DateTimeFormatter TRAFFIC_TIME_FORMAT = DateTimeFormat.forPattern("HH:mm");
    public static final Map<Integer, String> COLOR_CLASSES = new HashMap<Integer, String>() {{
        put(0, "gn");
        put(1, "gn");
        put(2, "gn");
        put(3, "gn");
        put(4, "yw");
        put(5, "yw");
        put(6, "yw");
        put(7, "rd");
        put(8, "rd");
        put(9, "rd");
        put(10, "rd");
    }};
    public static final Map<Integer, String> BE_DESCR = new HashMap<Integer, String>() {{
        put(3, "Месцамі перашкоды");
        put(4, "Месцамі перашкоды");
        put(6, "Рух абцяжараны");
    }};
    public static final Map<Integer, String> TT_DESCR = new HashMap<Integer, String>() {{
        put(0, "Юллар буш");
        put(1, "Юллар буш");
        put(2, "Юллар буш диярлек");
        put(3, "Урыннары белән тыгыз");
        put(4, "Урыннары белән тыгыз");
        put(5, "Тыгыз хәрәкәт");
        put(6, "Кыенлашкан хәрәкәт ");
        put(7, "Зур бөкеләр");
        put(8, "Күп километр озынлыгындагы бөкеләр");
        put(9, "Шәһәрдә хәрәкәт тукталып тора");
        put(10, "Җәяү тизрәк");
    }};
    public static final LocalDateTime WORK_TIME = new LocalDateTime()
            .withHourOfDay(3)
            .withMinuteOfHour(0)
            .withSecondOfMinute(0)
            .withMillisOfSecond(0);
    public static final LocalDateTime HOME_TIME = new LocalDateTime(WORK_TIME)
            .withHourOfDay(15);
    public static final int TRAFFIC_DIRECTION_DELAY_MINUTES = 10;
    public static final Interval WORK_INTERVAL =
            new Interval(WORK_TIME.plusMinutes(TRAFFIC_DIRECTION_DELAY_MINUTES).toDateTime(),
                    HOME_TIME.minusMinutes(TRAFFIC_DIRECTION_DELAY_MINUTES).toDateTime());
    public static final Interval HOME_INTERVAL =
            new Interval(HOME_TIME.plusMinutes(TRAFFIC_DIRECTION_DELAY_MINUTES).toDateTime(),
                    HOME_TIME.plusDays(1).minusMinutes(TRAFFIC_DIRECTION_DELAY_MINUTES).toDateTime());

    static {
        TRAFFIC_REGIONS_ALL.addAll(TRAFFIC_REGIONS_MAIN);
        TRAFFIC_REGIONS_ALL.addAll(TRAFFIC_REGIONS_TR);
    }

    public static boolean isFutureEnabled(Region region) {
        return export(MordaExports.TRAFFIC_FORECAST_MXNET, geo(region.getRegionIdInt())) != null;
    }

    @Step
    public static void shouldHaveFuture(Traffic traffic) {
        LocalTime current = TRAFFIC_TIME_FORMAT.parseLocalTime(traffic.getTime());

        if (current.plusMinutes(9).getHourOfDay() >= 8 && current.getHourOfDay() < 23) {
            shouldMatchTo(traffic, anyOf(
                    having(on(Traffic.class).getFuture(), not(empty())),
                    having(on(Traffic.class).getFutureLast(), notNullValue()),
                    having(on(Traffic.class).getFutureNext(), notNullValue())
            ));
            if (traffic.getFuture().size() > 0) {
                for (Future future : traffic.getFuture()) {
                    shouldHaveParameter(future, having(on(Future.class).getJams(),
                            allOf(greaterThanOrEqualTo(0), lessThanOrEqualTo(10))));
                    shouldHaveParameter(future,
                            having(on(Future.class).getHour(), greaterThan(current.getHourOfDay())));
                }
            } else {
                shouldMatchTo(Integer.parseInt(traffic.getFutureLast()), notNullValue());
                shouldMatchTo(Integer.parseInt(traffic.getFutureLast()), greaterThan(current.getHourOfDay()));
            }
        } else {
            shouldHaveParameter(traffic, having(on(Traffic.class).getFuture(), empty()));
            shouldHaveParameter(traffic, having(on(Traffic.class).getFutureLast(), nullValue()));
            shouldHaveParameter(traffic, having(on(Traffic.class).getFutureNext(), nullValue()));
        }
    }

    @Step
    public static String getDescr(int rate, Language language) {
//        if (language.equals(Language.BE) && BE_DESCR.containsKey(rate)) {
//            return BE_DESCR.get(rate);
//        if (language.equals(Language.TT) && TT_DESCR.containsKey(rate)) {
//            return TT_DESCR.get(rate);
//        } else {
        return getTranslation("maps_api", "Traffic", "level" + rate, language);
//        }
    }

    public static boolean skipDirection(LocalDateTime time) {
        return !(HOME_INTERVAL.contains(time.toDateTime()) || WORK_INTERVAL.contains(time.toDateTime()));
    }

    public static Matcher<String> getDirectionMatcher(LocalDateTime time) {
        if (HOME_INTERVAL.contains(time.toDateTime())) {
            return equalTo("home");
        } else if (WORK_INTERVAL.contains(time.toDateTime())) {
            return equalTo("work");
        }
        return not(isEmptyOrNullString());
    }

    public static void shouldHaveDescriptionOrInfo(TrafinfoEntry trafinfoEntry, Cleanvars cleanvars, Client client,
                                                   Region region, Language language, UserAgent userAgent)
            throws IOException {
        if (trafinfoEntry != null) {
            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getInformer(), notNullValue()));
            shouldMatchTo(cleanvars.getTraffic().getInformer(), allOf(
                    having(on(Informer.class).getGeo(), equalTo(trafinfoEntry.getGeo())),
                    having(on(Informer.class).getText(), equalTo(trafinfoEntry.getText())),
                    having(on(Informer.class).getLang(), equalTo(trafinfoEntry.getLang())),
                    having(on(Informer.class).getFrom(), equalTo(trafinfoEntry.getFrom())),
                    having(on(Informer.class).getTill(), equalTo(trafinfoEntry.getTill())),
                    having(on(Informer.class).getDomain(), equalTo(trafinfoEntry.getDomain())),
                    having(on(Informer.class).getLink(),
                            equalTo(userAgent.isMobile() ? trafinfoEntry.getMob() : trafinfoEntry.getLink())),
                    having(on(Informer.class).getMob(), equalTo(trafinfoEntry.getMob())),
                    having(on(Informer.class).getReason(), equalTo(trafinfoEntry.getReason()))
            ));
            shouldHaveResponseCode(client, cleanvars.getTraffic().getInformer().getLink(), equalTo(200));
        } else if (cleanvars.getTraffic().getInformer() != null) {
            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getInformer(), notNullValue()));
            shouldHaveParameter(cleanvars.getTraffic(),
                    having(on(Traffic.class).getInformer().getLink(), not(isEmptyOrNullString())));
            shouldHaveResponseCode(client, cleanvars.getTraffic().getInformer().getLink(), equalTo(200));
        } else if (!region.getDomain().equals(COM_TR) &&
                cleanvars.getTraffic().getFutureEndDay() == 1 &&
                cleanvars.getTraffic().getRate() <= 3) {
            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getDescr(), nullValue()));
        } else {
            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getDescr(),
                    equalTo(getDescr(cleanvars.getTraffic().getRate(), language))));
        }
    }
}
