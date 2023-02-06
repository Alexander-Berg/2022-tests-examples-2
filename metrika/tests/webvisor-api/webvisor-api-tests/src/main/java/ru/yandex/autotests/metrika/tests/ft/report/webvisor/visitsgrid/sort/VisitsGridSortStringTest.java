package ru.yandex.autotests.metrika.tests.ft.report.webvisor.visitsgrid.sort;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataVisitsGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.VisitsGridParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.*;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.matchers.OrderMatcher.isAscendingOrdered;
import static ru.yandex.autotests.irt.testutils.matchers.OrderMatcher.isDescendingOrdered;
import static ru.yandex.autotests.metrika.commons.rules.IgnoreParameters.Tag;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.AT_NEW_WEBVISOR;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.DIRECT;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.matchers.Matchers.isUtf8Ordered;
import static ru.yandex.autotests.metrika.matchers.SortMatcher.isSortEqualTo;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by konkov on 16.06.2015.
 */
@Features(Requirements.Feature.WEBVISOR)
@Stories({Requirements.Story.WebVisor.VISITS_GRID})
@Title("Вебвизор: таблица визитов, сортировка")
@RunWith(Parameterized.class)
public class VisitsGridSortStringTest {

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    private static final List<Counter> COUNTERS = of(DIRECT, AT_NEW_WEBVISOR);

    private static final String START_DATE = "14daysAgo";
    private static final String END_DATE = "yesterday";

    private final static UserSteps user = new UserSteps();

    private static List<String> requiredDimensionNames;

    @Parameter
    public String dimensionName;

    @Parameter(1)
    public Counter counter;

    private VisitsGridParameters reportParameters;

    @Parameters(name = "Счетчик: {1}, измерения: {0}")
    public static Collection createParameters() {
        return CombinatorialBuilder.builder()
                .values(
                        user.onWebVisorMetadataSteps()
                                .getWebVisorVisitSortableDimensions(not(isIn(asList("integer", "duration", "visit-activity"))))
                                .stream().filter(d -> !d.equals("ym:s:labelsAggregated")).collect(toList())//TESTIRT-6111
                )
                .values(COUNTERS)
                .build();
    }

    @BeforeClass
    public static void init() {
        requiredDimensionNames = user.onWebVisorMetadataSteps().getWebVisorDefaultVisitDimensions().getRequired();
    }

    @Before
    public void setup() {
        reportParameters = new VisitsGridParameters()
                .withId(counter.get(ID))
                .withDimensions(requiredDimensionNames, dimensionName)
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withFilters(dimension(dimensionName).defined().build());
    }

    @Test
    @IgnoreParameters(reason = "no data", tag = "no data")
    public void visitsGridSortAscendingTest() {
        reportParameters.setSort(sort().by(dimensionName).build());

        WebvisorV2DataVisitsGETSchema report = user.onWebVisorSteps().getVisitsGridAndExpectSuccess(reportParameters);

        assumeThat("данные для теста присутствуют", report,
                having(on(WebvisorV2DataVisitsGETSchema.class).getData(), iterableWithSize(greaterThan(0))));


        assumeThat("сортировка соответствует заданной", report.getQuery().getSort(),
                isSortEqualTo(reportParameters.getSort()));

        List<String> dimensionValues = user.onResultSteps().getDimensionValues(dimensionName, report);

        assertThat("значения измерения упорядочены", dimensionValues, isUtf8Ordered(isAscendingOrdered()));
    }

    @Test
    @IgnoreParameters(reason = "no data", tag = "no data")
    public void visitsGridSortDescendingTest() {
        reportParameters.setSort(sort().by(dimensionName).descending().build());

        WebvisorV2DataVisitsGETSchema report = user.onWebVisorSteps().getVisitsGridAndExpectSuccess(reportParameters);

        assumeThat("данные для теста присутствуют", report,
                having(on(WebvisorV2DataVisitsGETSchema.class).getData(), iterableWithSize(greaterThan(0))));

        assumeThat("сортировка соответствует заданной", report.getQuery().getSort(),
                isSortEqualTo(reportParameters.getSort()));

        List<String> dimensionValues = user.onResultSteps().getDimensionValues(dimensionName, report);

        assertThat("значения измерения упорядочены", dimensionValues, isUtf8Ordered(isDescendingOrdered()));
    }

    @Tag(name = "no data")
    public static Collection<Object[]> ignoreParametersNoData() {
        return asList(new Object[][]{
                {"ym:s:WVAdvEngine", AT_NEW_WEBVISOR},
                {"ym:s:searchPhraseWithLink", AT_NEW_WEBVISOR}
        });
    }

}
