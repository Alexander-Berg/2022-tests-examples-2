package ru.yandex.autotests.mordabackend.logo;

import org.apache.commons.lang3.time.DateUtils;
import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;
import ru.yandex.autotests.mordaexportsclient.beans.LogoV14Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.select;
import static org.hamcrest.Matchers.allOf;
import static ru.yandex.autotests.mordabackend.logo.LogoUtils.ValidLogoEntryMatcher.isValid;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.*;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.getRegionParents;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.utils.morda.language.Language.*;
import static ru.yandex.autotests.utils.morda.region.Region.*;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21.07.14
 */
public class LogoUtils {

    public static final List<Language> LANGUAGES = Arrays.asList(RU, UK, BE, KK, TT);
    public static final List<Region> LOGO_REGIONS_MAIN = Arrays.asList(
            SANKT_PETERBURG, MOSCOW, KIEV, HARKOV, MINSK, ASTANA, NIZHNIY_NOVGOROD, EKATERINBURG, LYUDINOVO, SIMFEROPOL
    );

    public static final List<Region> LOGO_REGIONS_TR = Arrays.asList(
            ISTANBUL, BURSA, ALANYA, ANTALYA, IZMIR, ADANA, GAZIANTEP, MERSIN
    );

    public static final List<Region> LOGO_REGIONS_ALL = new ArrayList<>();
    static {
        LOGO_REGIONS_ALL.addAll(LOGO_REGIONS_TR);
        LOGO_REGIONS_ALL.addAll(LOGO_REGIONS_MAIN);
    }

    public static LogoV14Entry getLogoEntry(Region region, Language language, String hiddenTime) throws ParseException {
        List<Integer> regionParents = getRegionParents(region.getRegionIdInt());
        for (int gid : regionParents) {
            MordaExport<LogoV14Entry> logoExport = region.getDomain().equals(Domain.COM_TR) ? LOGO_NEW : LOGO_V14;
            List<LogoV14Entry> entries = select(exports(logoExport, domain(region.getDomain())), allOf(
                    having(on(LogoV14Entry.class).getGeos(), matches("(^|.*,\\s)" + String.valueOf(gid) + "($|,\\s.*)")),
                    lang(language),
                    isValid(hiddenTime)
            ));
            if (!entries.isEmpty()) {
                return entries.get(0);
            }
        }
        return null;
    }

    protected static class ValidLogoEntryMatcher extends TypeSafeMatcher<LogoV14Entry> {
        private String hiddenTime;

        private ValidLogoEntryMatcher(String hiddenTime) {
            this.hiddenTime = hiddenTime;
        }

        public static ValidLogoEntryMatcher isValid(String hiddenTime) {
            return new ValidLogoEntryMatcher(hiddenTime);
        }

        @Override
        protected boolean matchesSafely(LogoV14Entry entry) {
            try {
                final Date localTime = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").parse(hiddenTime);
                final Date from = new SimpleDateFormat("yyyy-MM-dd").parse(entry.getFrom());
                final Date to = DateUtils.addDays(new SimpleDateFormat("yyyy-MM-dd").parse(entry.getTill()), 1);
                return localTime.after(from) && localTime.before(to);
            } catch (ParseException e) {
                throw new RuntimeException(e);
            }
        }

        @Override
        public void describeTo(Description description) {
        }
    }
}
