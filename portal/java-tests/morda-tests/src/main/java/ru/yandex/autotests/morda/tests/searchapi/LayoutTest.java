package ru.yandex.autotests.morda.tests.searchapi;

import org.hamcrest.collection.IsIn;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.api.search.v1.SearchApiV1Request;
import ru.yandex.autotests.morda.api.search.v2.SearchApiV2Request;
import ru.yandex.autotests.morda.beans.api.search.v1.SearchApiV1Response;
import ru.yandex.autotests.morda.beans.api.search.v2.LayoutApiV2;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.geobase.regions.Belarus;
import ru.yandex.geobase.regions.Kazakhstan;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Ukraine;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Stream;

import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.everyItem;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.ALL;
import static ru.yandex.autotests.morda.steps.CheckSteps.checkBean;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.NIZHNY_NOVGOROD;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 08/11/16
 */
@Aqua.Test(title = "Данные SearchApi-v2 Layout")
@Features({MordaTestTags.SEARCH_API, MordaTestTags.V2, MordaTestTags.LAYOUT})
@RunWith(Parameterized.class)
public class LayoutTest {
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();

    protected static final Set<String> ALLOWED_LAYOUT = new HashSet<>(asList(
            "search", "now", "informer", "topnews", "weather", "video", "bridges", "stocks", "poi",
            "transport", "tv", "afisha", "services", "transportmap", "radio"
    ));

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();
    private SearchApiRequestData requestData;

    public LayoutTest(SearchApiRequestData requestData) {
        this.requestData = requestData;
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<SearchApiRequestData> data() {
        return Stream.of(
                Russia.MOSCOW, Russia.SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.VLADIVOSTOK, Russia.YEKATERINBURG,
                Russia.DUBNA, Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, NIZHNY_NOVGOROD, Russia.SAMARA,
                Belarus.MINSK, Belarus.GOMEL,
                Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV,
                Kazakhstan.ALMATY, ASTANA
        )
                .map(region -> new SearchApiRequestData().setGeo(region).setLanguage(MordaLanguage.RU).setBlock(ALL))
                .collect(toList());
    }

    @Test
    public void allowedLayoutIdsV2() {
        SearchApiV2Response response = new SearchApiV2Request(CONFIG.pages().getEnvironment(), requestData).read();
        List<String> layoutIds = response.getLayout().stream()
                .map(LayoutApiV2::getId)
                .collect(toList());

        checkBean(layoutIds, everyItem(IsIn.isIn(ALLOWED_LAYOUT)));
    }

//    @Test
    public void allowedLayoutIdsV1() {
        SearchApiV1Response response = new SearchApiV1Request(CONFIG.pages().getEnvironment(), requestData).read();
        List<String> layoutIds = response.getLayout();

        checkBean(layoutIds, everyItem(IsIn.isIn(ALLOWED_LAYOUT)));
    }
}
