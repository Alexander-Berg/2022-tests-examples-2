package ru.yandex.autotests.mordabackend.disaster;

import ch.lambdaj.function.convert.Converter;
import org.apache.commons.collections.CollectionUtils;
import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordaexportsclient.MordaExportClient;
import ru.yandex.autotests.mordaexportsclient.beans.DisasterV12Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import java.net.URI;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;

import static ch.lambdaj.Lambda.convert;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.DISASTER_V12;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.DISASTER_MOBILE;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.*;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29.07.14
 */
public class DisasterUtils {

    private static final Properties CONFIG = new Properties();

    public static final List<Region> DISASTER_REGIONS_MAIN = Arrays.asList(
            MOSCOW, KIEV, SANKT_PETERBURG, MINSK, EKATERINBURG, PERM,
            SAMARA, CHELYABINSK, NOVOSIBIRSK, DUBNA, ASTANA, ALMATY,
            VLADIVOSTOK, UFA, YAROSLAVL, HARKOV, DNEPROPETROVSK, KAZAN
    );

    public static final List<Region> DISASTER_REGIONS_TR = Arrays.asList(
            ISTANBUL, BURSA, ALANYA, ANTALYA, IZMIR, ADANA, GAZIANTEP, MERSIN
    );

    public static final List<Region> DISASTER_REGIONS_ALL = new ArrayList<>();
    static {
        DISASTER_REGIONS_ALL .addAll(DISASTER_REGIONS_MAIN);
        DISASTER_REGIONS_ALL .addAll(DISASTER_REGIONS_TR);
    }

    public static final List<Language> LANGUAGES = Arrays.asList(RU, UK, BE, KK, TT);

    public static DisasterV12Entry getDisasterEntry(Region region, Language language, UserAgent userAgent, String time)
            throws ParseException {
        final MordaExportClient mordaExportClient = new MordaExportClient(URI.create(CONFIG.getBaseURL()));
        final Date localTime = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").parse(time);

        if (userAgent.isMobile()) {
            return export(DISASTER_MOBILE, lang(language), domain(region.getDomain()),
                    having(on(DisasterV12Entry.class).getContent(),
                            equalTo(userAgent.getIsTouch() == 1 ? "touch" : "pda")),
                    new IsValidDisaster(localTime, mordaExportClient.getRegionParents(
                            MordaClient.getJsonEnabledClient(), region.getRegionIdInt()).getGeo()));
        } else {
            return export(DISASTER_V12, lang(language), domain(region.getDomain()),
                    new IsValidDisaster(localTime, mordaExportClient.getRegionParents(
                            MordaClient.getJsonEnabledClient(), region.getRegionIdInt()).getGeo()));
        }
    }

    private static class IsValidDisaster extends TypeSafeMatcher<DisasterV12Entry> {
        private Date now;
        private List<Integer> regions;

        private IsValidDisaster(Date now, List<Integer> regions) {
            this.now = now;
            this.regions = regions;
        }

        @Override
        protected boolean matchesSafely(DisasterV12Entry item) {
            Date from = null;
            Date to = null;
            try {
                from = parseDisasterDate(item.getFrom());
                to = parseDisasterDate(item.getTill());
            } catch (ParseException e) {
                throw new RuntimeException(e);

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

        private Date parseDisasterDate(String date) throws ParseException {
            try {
                return new SimpleDateFormat("yyyy-MM-dd HH:mm").parse(date);
            } catch (ParseException e) {
                return new SimpleDateFormat("yyyy-MM-dd").parse(date);
            }
        }

        @Override
        public void describeTo(Description description) {
        }
    }
}
