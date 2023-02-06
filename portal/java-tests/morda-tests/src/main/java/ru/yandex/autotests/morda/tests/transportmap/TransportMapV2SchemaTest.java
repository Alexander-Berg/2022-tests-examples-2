package ru.yandex.autotests.morda.tests.transportmap;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.api.search.v2.SearchApiV2Request;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.tests.AbstractSchemaTest;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.qatools.Tag;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.TRANSPORTMAP;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/08/16
 */
@Aqua.Test(title = "Схема SearchApi-v2 TransportMap")
@Features({MordaTestTags.SEARCH_API, MordaTestTags.V2, MordaTestTags.TRANSPORTMAP})
@RunWith(Parameterized.class)
@Tag("sandbox")
public class TransportMapV2SchemaTest extends AbstractSchemaTest {
    private static final String JSON_SCHEMA_FILE = "/api/search/2/transportmap/transportmap-response.json";

    public TransportMapV2SchemaTest(SearchApiRequestData requestData) {
        super(new SearchApiV2Request(CONFIG.pages().getEnvironment(), requestData)
                .header("X-Yandex-TestExp","transportmap")
                .header("X-Yandex-TestExpForceDisabled","1"),
                JSON_SCHEMA_FILE);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<SearchApiRequestData> data() {
        List<SearchApiRequestData> data = new ArrayList<>();
        for (GeobaseRegion region : asList(
                Russia.MOSCOW, Russia.SAINT_PETERSBURG, Russia.KALUGA,
                Russia.LIPETSK
        )) {
            for (MordaLanguage language : asList(RU, UK, BE, KK)) {
                data.add(new SearchApiRequestData().setGeo(region).setLanguage(language).setBlock(TRANSPORTMAP).setAppVersion("5070000"));
            }
        }
        return data;
    }
}
