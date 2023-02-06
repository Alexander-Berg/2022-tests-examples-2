package ru.yandex.autotests.mordabackend.mobile.poi;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.poi.PoiItem;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.parameters.PoiParameterProvider;
import ru.yandex.autotests.mordaexportsclient.beans.Poi2Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.POI;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.ANDROID_HTC_SENS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.attach;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.language.Language.*;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslationSafely;
import static ru.yandex.autotests.utils.morda.region.Region.*;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encodeRequest;

/**
 * User: ivannik
 * Date: 22.08.2014
 */
//@Aqua.Test(title = "Poi Mobile Items")
//@Features("Mobile")
//@Stories("Poi Mobile Items")
//@RunWith(CleanvarsParametrizedRunner.class)
public class PoiItemsBlockTest {

//    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}, {6}")
    public static ParametersUtils parameters =
            parameters(SANKT_PETERBURG, MOSCOW, KIEV, HARKOV, MINSK, ASTANA, NIZHNIY_NOVGOROD, EKATERINBURG, LYUDINOVO)
                    .withLanguages(RU, UK, BE, KK, TT)
                    .withUserAgents(TOUCH, ANDROID_HTC_SENS)
                    .withParameterProvider(new PoiParameterProvider())
                    .withCleanvarsBlocks(POI);

    private Language language;
    private PoiItem poiItem;
    private Poi2Entry poi2Entry;

    public PoiItemsBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                             Language language, UserAgent userAgent, String poiId, Poi2Entry poi2Entry) {
        this.language = language;
        this.poi2Entry = poi2Entry;
        this.poiItem = selectFirst(cleanvars.getPoi().getList(), having(on(PoiItem.class).getId(), equalTo(poiId)));
        attach(poiItem);
    }

//    @Test
    public void poiItem() {
        String description = getTranslation("home", "mobile", "poi.category." + poi2Entry.getId(), language);
        String text = getTranslationSafely("home", "mobile", "poi.search." + poi2Entry.getId(), language);

        shouldHaveParameter(poiItem, allOfDetailed(
                hasPropertyWithValue(on(PoiItem.class).getBig(), equalTo(poi2Entry.getBig())),
                hasPropertyWithValue(on(PoiItem.class).getPromo(), equalTo(poi2Entry.getPromo())),
                hasPropertyWithValue(on(PoiItem.class).getDescription(), equalTo(description)),
                hasPropertyWithValue(on(PoiItem.class).getText(), equalTo(text)),
                hasPropertyWithValue(on(PoiItem.class).getTextUri(), equalTo(encodeRequest(text)))
        ));
    }

}
