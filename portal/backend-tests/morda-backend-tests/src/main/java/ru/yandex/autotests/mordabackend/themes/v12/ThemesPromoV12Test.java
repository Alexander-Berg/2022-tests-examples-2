package ru.yandex.autotests.mordabackend.themes.v12;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.util.Collection;

import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.*;

/**
 * User: ivannik
 * Date: 29.07.2014
 */

public class ThemesPromoV12Test {

    @Parameterized.Parameters(name = "{3}, {4}")
    public static Collection<Object[]> data() {
        return parameters(RU, UA, KZ, BY)
                .withLanguages(Language.RU, Language.UK, Language.KK, Language.TT, Language.BE)
                .build();
    }

    private final Cleanvars cleanvars;
//    private final List<ThemesPromoEntry> promoExports;

    public ThemesPromoV12Test(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                             Language language) {
        this.cleanvars = cleanvars;
//        this.promoExports =
//                exports(THEMES_PROMO_V12, domain(region.getDomain()), lang(language), geo(region.getRegionIdInt()),
//                        having(on(ThemesPromoEntry.class).getFrom(), before(cleanvars.getYYYYMMDD())),
//                        having(on(ThemesPromoEntry.class).getTo(), after(cleanvars.getYYYYMMDD())));
    }

//    @Test
//    public void themesPromo() {
//        assumeThat("No promos", promoExports, not(empty()));
//        if (cleanvars.getDisaster().getNoPromo() == 1) {
//            assertThat("Wrong promo collection size", cleanvars.getThemes().getPromos(), hasSize(0));
//        } else {
//            assertThat("Wrong promo collection size", cleanvars.getThemes().getPromos(), hasSize(promoExports.size()));
//            for (Promo promo : cleanvars.getThemes().getPromos()) {
//                shouldMatchTo(promo, allOf(
//                        having(on(Promo.class).getCounter(),
//                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getCounter()))),
//                        having(on(Promo.class).getGroup(),
//                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getGroup()))),
//                        having(on(Promo.class).getGroupTmp(),
//                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getGroupTmp()))),
//                        having(on(Promo.class).getTitle(),
//                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getTitle()))),
//                        having(on(Promo.class).getBk(),
//                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getBk()))),
//                        having(on(Promo.class).getText(),
//                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getText()))),
//                        having(on(Promo.class).getThemes(),
//                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getThemes()))),
//                        having(on(Promo.class).getSet(),
//                                isIn(extract(promoExports, on(ThemesPromoEntry.class).getSet())))
//                ));
//            }
//        }
//    }
}
