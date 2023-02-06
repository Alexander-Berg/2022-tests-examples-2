package ru.yandex.autotests.mordabackend.mobile.poi;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;

import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.POI;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.ANDROID_HTC_SENS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.attach;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.language.Language.*;
import static ru.yandex.autotests.utils.morda.region.Region.*;

/**
 * User: ivannik
 * Date: 22.08.2014
 */
//@Aqua.Test(title = "Poi Mobile")
//@Features("Mobile")
//@Stories("Poi Mobile")
//@RunWith(CleanvarsParametrizedRunner.class)
public class PoiBlockTest {

//    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(SANKT_PETERBURG, MOSCOW, KIEV, HARKOV, MINSK, ASTANA, NIZHNIY_NOVGOROD, EKATERINBURG, LYUDINOVO)
                    .withLanguages(RU, UK, BE, KK, TT)
                    .withUserAgents(TOUCH, ANDROID_HTC_SENS)
                    .withCleanvarsBlocks(POI);

    private Cleanvars cleanvars;
    private Region region;
    private Language language;
    private UserAgent userAgent;

    public PoiBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                         Language language, UserAgent userAgent) {
        this.cleanvars = cleanvars;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
        attach(cleanvars.getPoi());
    }

//    @Test
    public void poiList() {
//        List<String> expectedItems = extract(
//                getPoiItems(region, language, userAgent),
//                on(Poi2Entry.class).getId());
//        List<String> actualItems = extract(
//                cleanvars.getPoi().getList(),
//                on(PoiItem.class).getId());
//
//        shouldMatchTo(actualItems, hasSameItemsAsCollection(expectedItems));
    }

//    @Test
    public void poiPromoList() {
//        List<String> expectedItems = extract(
//                getPoiPromoItems(region, language, userAgent),
//                on(Poi2Entry.class).getId());
//        List<String> actualItems = extract(
//                cleanvars.getPoi().getPromo(),
//                on(PoiItem.class).getId());
//
//        shouldMatchTo(actualItems, hasSameItemsAsCollection(expectedItems));
    }
}
