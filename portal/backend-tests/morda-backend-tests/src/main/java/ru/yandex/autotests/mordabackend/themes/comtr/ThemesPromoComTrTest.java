package ru.yandex.autotests.mordabackend.themes.comtr;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.themes.Promo;
import ru.yandex.autotests.mordaexportsclient.beans.ThemesPromoEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.after;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.before;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.THEMES_PROMO_COMTR;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: ivannik
 * Date: 29.07.2014
 */

public class ThemesPromoComTrTest {

    @Parameterized.Parameters(name = "{3}, {4}")
    public static Collection<Object[]> data() {
        return parameters(COM_TR).withLanguages(Language.TR).build();
    }

    private final Cleanvars cleanvars;
    private final List<ThemesPromoEntry> promoExports;

    public ThemesPromoComTrTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                Language language) {
        this.cleanvars = cleanvars;
        this.promoExports =
                exports(THEMES_PROMO_COMTR, domain(region.getDomain()), lang(language), geo(region.getRegionIdInt()),
                        having(on(ThemesPromoEntry.class).getFrom(), before(cleanvars.getYYYYMMDD())),
                        having(on(ThemesPromoEntry.class).getTo(), after(cleanvars.getYYYYMMDD())));
    }

//    @Test
    public void themesPromo() {
        assumeThat("No promos", promoExports, not(empty()));
        if (cleanvars.getDisaster().getNoPromo() == 1) {
            assertThat("Wrong promo collection size", cleanvars.getThemes().getPromos(), hasSize(0));
        } else {
            assertThat("Wrong promo collection size", cleanvars.getThemes().getPromos(), hasSize(promoExports.size()));
            for (Promo promo : cleanvars.getThemes().getPromos()) {
                shouldMatchTo(promo, allOf(
                        having(on(Promo.class).getCounter(),
                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getCounter()))),
                        having(on(Promo.class).getGroup(),
                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getGroup()))),
                        having(on(Promo.class).getGroupTmp(),
                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getGroupTmp()))),
                        having(on(Promo.class).getTitle(),
                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getTitle()))),
                        having(on(Promo.class).getBk(),
                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getBk()))),
                        having(on(Promo.class).getText(),
                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getText()))),
                        having(on(Promo.class).getThemes(),
                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getThemes()))),
                        having(on(Promo.class).getSet(),
                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getSet())))
                ));
            }
        }
    }
}
