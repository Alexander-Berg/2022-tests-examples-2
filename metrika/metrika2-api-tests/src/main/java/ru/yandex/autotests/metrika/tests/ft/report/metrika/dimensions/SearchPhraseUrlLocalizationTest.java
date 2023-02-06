package ru.yandex.autotests.metrika.tests.ft.report.metrika.dimensions;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.everyItem;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.requestDomain;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.DIMENSIONS})
@Title("Локализация URL поисковой фразы")
@RunWith(Parameterized.class)
public class SearchPhraseUrlLocalizationTest {

    private static final String METRIC = "ym:s:visits";
    private static final String SEARCH_PHRASE_DIM = "ym:s:searchPhrase";
    private static final String SEARCH_ENGINE_DIM = "ym:s:searchEngine";
    private static final String START_DATE = "2017-03-01";
    private static final String END_DATE = "2017-03-10";

    private UserSteps user = new UserSteps().withDefaultAccuracy();

    private List<String> searchPhraseUrls;

    @Parameterized.Parameter
    public String searchEngine;

    @Parameterized.Parameter(1)
    public String requestDomain;

    @Parameterized.Parameter(2)
    public String expectedSearchPhraseDomain;

    @Parameterized.Parameters(name = "Поисковой движок: {0}, домен: {1}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values("yandex_search", "yandex_mobile", "yandex_mobile_app")
                .vectorValues(
                        of("ru", "yandex.ru"),
                        of("com", "yandex.com"),
                        of("ua", "yandex.ua"),
                        of("by", "yandex.by"),
                        of("kz", "yandex.kz"),
                        of("tr", "yandex.com.tr"),
                        of("", "yandex.ru")
                )
                .build();
    }

    @Before
    public void init() {
        StatV1DataGETSchema report = user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withId(YANDEX_METRIKA_2_0)
                        .withMetric(METRIC)
                        .withDimension(SEARCH_PHRASE_DIM)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)
                        .withFilters(dimension(SEARCH_ENGINE_DIM)
                                .equalTo(searchEngine)
                                .build()),
                requestDomain(requestDomain)
        );

        searchPhraseUrls = report.getData().stream()
                .map(row -> row.getDimensions().get(0).get("url"))
                .collect(toList());
    }

    @Test
    public void check() {
        assertThat(
                "URL-ы поисковых фраз содержат домен " + expectedSearchPhraseDomain,
                searchPhraseUrls,
                everyItem(containsString(expectedSearchPhraseDomain))
        );
    }
}
