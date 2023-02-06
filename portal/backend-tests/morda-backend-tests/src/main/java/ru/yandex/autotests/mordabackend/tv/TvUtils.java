package ru.yandex.autotests.mordabackend.tv;

import ch.lambdaj.function.convert.Converter;
import org.apache.commons.collections.CollectionUtils;
import org.apache.commons.lang.math.IntRange;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import org.joda.time.DateTime;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.local.LocalBlock;
import ru.yandex.autotests.mordabackend.beans.tv.Tv;
import ru.yandex.autotests.mordabackend.beans.tv.TvEvent;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordaexportsclient.MordaExportClient;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.mordaexportsclient.beans.TvAnnouncesEntry;
import ru.yandex.autotests.utils.morda.region.Region;

import java.net.URI;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static ch.lambdaj.Lambda.convert;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.TV_ANNOUNCES;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
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
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MERSIN;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.NOVOSIBIRSK;
import static ru.yandex.autotests.utils.morda.region.Region.PERM;
import static ru.yandex.autotests.utils.morda.region.Region.SAMARA;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;
import static ru.yandex.autotests.utils.morda.region.Region.UFA;
import static ru.yandex.autotests.utils.morda.region.Region.VLADIVOSTOK;
import static ru.yandex.autotests.utils.morda.region.Region.YAROSLAVL;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 08.07.14
 */
public class TvUtils {
    private static final Properties CONFIG = new Properties();

    public static final List<Region> TV_REGIONS_MAIN = Arrays.asList(
            MOSCOW, KIEV, SANKT_PETERBURG, MINSK, EKATERINBURG, PERM,
            SAMARA, CHELYABINSK, NOVOSIBIRSK, DUBNA, ASTANA, ALMATY,
            VLADIVOSTOK, UFA, YAROSLAVL, HARKOV, DNEPROPETROVSK);


    public static final List<Region> TV_REGIONS_TR = Arrays.asList(
            ISTANBUL, BURSA, ALANYA, ANTALYA, IZMIR, ADANA, GAZIANTEP, MERSIN
    );

    public static final List<Region> TV_REGIONS_ALL = new ArrayList<>();

    static {
        TV_REGIONS_ALL.addAll(TV_REGIONS_MAIN);
    }

    public static final int TV_ANNOUNCE_SIZE = 1;
    public static final int TV_EVENTS_DAY = 6;
    public static final int TV_EVENTS_EVENING_AND_WEEKEND = 6;
    private static final String TV_EVENTS_HREF_PATTERN = "%sprogram/\\d+\\?eventId=\\d+";
    private static final String TV_HREF_PATTERN = "%s%s/";
    private static final String TR_TV_HREF = "https://tv.yandex.com.tr/983/";
    private static final String TR_MOBILE_TV_HREF = "https://m.tv.yandex.com.tr/983/";
    private static final String TV_EVENTS_CH_HREF_PATTERN = "%schannels/%s";

    public static IntRange getDayHourRange(int dayOfWeek) {
        switch (dayOfWeek) {
            case 5:
                return new IntRange(3, 17);
            case 6:
                return new IntRange(3, 9);
            case 7:
                return new IntRange(3, 9);
            default:
                return new IntRange(3, 16);
        }
    }

    private static final IntRange COMMON_DAY_RANGE = new IntRange(3, 15);

    public static int getTvEventsNumber(Tv tv) {
        if (tv.getEveningMode() == 1 || tv.getWeekendMode() == 1) {
            return TV_EVENTS_EVENING_AND_WEEKEND;
        } else {
            return TV_EVENTS_DAY;
        }
    }

    public static Matcher<Integer> getEveningModeMatcher(LocalBlock local, String isHoliday) {
        if (local.getWday() + 1 == Calendar.MONDAY && local.getHour() < COMMON_DAY_RANGE.getMinimumInteger()
                || local.getWday() + 1 == Calendar.SATURDAY && local.getHour() >= COMMON_DAY_RANGE.getMinimumInteger()
                || local.getWday() + 1 == Calendar.SUNDAY
                || "1".equals(isHoliday) && local.getHour() >= COMMON_DAY_RANGE.getMinimumInteger()) {
            return equalTo(0);
        }
        if (COMMON_DAY_RANGE.containsInteger(local.getHour())) {
            return equalTo(0);
        } else {
            return equalTo(1);
        }
    }

    private static final Map<Region, Region> TV_HREF_MAP = new HashMap<Region, Region>() {{
        put(DUBNA, MOSCOW);
    }};

    public static Matcher<String> getTvHrefMatcher(ServicesV122Entry entry, Region region, UserAgent userAgent) {

        if (entry == null && region.getDomain().equals(COM_TR)) {
            if (userAgent.isMobile()) {
                return equalTo(TR_MOBILE_TV_HREF);
            } else {
                return equalTo(TR_TV_HREF);
            }
        }

        String baseUrl;
        if (userAgent.isMobile()) {
            baseUrl = entry.getPda().startsWith("//")? "https:" + entry.getPda(): entry.getPda();
        } else {
            baseUrl = entry.getHref().startsWith("//")? "https:" + entry.getHref(): entry.getHref();
        }

        if (TV_HREF_MAP.containsKey(region)) {
            return matches(String.format(TV_HREF_PATTERN, baseUrl, TV_HREF_MAP.get(region).getRegionId()));
        }

        MordaExportClient mordaExportClient = new MordaExportClient(URI.create(CONFIG.getBaseURL()));
        List<Integer> parents = mordaExportClient.getRegionParents(
                MordaClient.getJsonEnabledClient(),
                region.getRegionIdInt()).getGeo();
        parents.add(213);
        List<Matcher<? super String>> allMatchers = new ArrayList<>();
        for (int parent : parents) {
            allMatchers.add(matches(String.format(TV_HREF_PATTERN, baseUrl, parent)));
        }
        return anyOf(allMatchers);
    }

    public static Matcher<String> getTvEventHrefMatcher(Cleanvars cleanvars) {
        return matches(String.format(TV_EVENTS_HREF_PATTERN, cleanvars.getTV().getHref()));
    }

    public static Matcher<String> getTvChHrefMatcher(Cleanvars cleanvars, String chId) {
        return matches(String.format(TV_EVENTS_CH_HREF_PATTERN, cleanvars.getTV().getHref(), chId));
    }

    public static void shouldSeeTvEventTitle(TvEvent event) {
        if (!event.getName().equals(event.getFull())) {
            shouldHaveParameter(event, having(on(TvEvent.class).getTitle(), not(isEmptyOrNullString())));
        }

        if (!event.getTitle().isEmpty()) {
            shouldHaveParameter(event, having(on(TvEvent.class).getTitle(), startsWith(event.getFull())));
        }
    }

    private static final Map<UserAgent, String> CONTENT_TYPES = new HashMap<UserAgent, String>() {{
        put(UserAgent.FF_34, "big");
        put(UserAgent.PDA, "mob");
        put(UserAgent.TOUCH, "touch");
    }};

    public static TvAnnouncesEntry getTvAnnounce(String time, final Region region, UserAgent userAgent)
            throws ParseException {
        final MordaExportClient mordaExportClient = new MordaExportClient(URI.create(CONFIG.getBaseURL()));
        final Date localTime = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").parse(time);

        return export(TV_ANNOUNCES,
                new IsValidAnnounce(localTime, mordaExportClient.getRegionParents(MordaClient.getJsonEnabledClient(),
                        region.getRegionIdInt()).getGeo()),
                having(on(TvAnnouncesEntry.class).getContent(), equalTo(CONTENT_TYPES.get(userAgent))));
    }

    private static class IsValidAnnounce extends TypeSafeMatcher<TvAnnouncesEntry> {
        private Date now;
        private List<Integer> regions;

        private IsValidAnnounce(Date now, List<Integer> regions) {
            this.now = now;
            this.regions = regions;
        }

        @Override
        protected boolean matchesSafely(TvAnnouncesEntry item) {
            Date from = DateTime.parse(item.getFrom()).toDate();
            Date to;
            if (item.getTo().contains(":")) {
                to = DateTime.parse(item.getTo()).toDate();
            } else {
                to = DateTime.parse(item.getTo()).plusDays(1).toDate();
            }
            if (from.before(now) && to.after(now)) {
                List<Integer> geoIds = convert(item.getGeos().split(","), new Converter<String, Integer>() {
                    @Override
                    public Integer convert(String from) {
                        return Integer.valueOf(from.trim());
                    }
                });
                if (!CollectionUtils.intersection(geoIds, regions).isEmpty()) {
                    return true;
                }
            }
            return false;
        }

        @Override
        public void describeTo(Description description) {
        }
    }

}
