package ru.yandex.autotests.metrika.tests.ft.report.webvisor.visitsgrid.filter;

import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataVisitsGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.VisitsGridParameters;
import ru.yandex.autotests.metrika.filters.Term;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static org.hamcrest.core.Every.everyItem;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.AT_NEW_WEBVISOR;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
import static ru.yandex.autotests.metrika.utils.AllureUtils.*;

/**
 * Created by konkov on 22.12.2014.
 */
@Features(Requirements.Feature.WEBVISOR)
@Stories({Requirements.Story.WebVisor.VISITS_GRID})
@Title("Вебвизор: таблица визитов, фильтрация по сложным измерениям")
@RunWith(Parameterized.class)
public class VisitsGridFilterComplexTest {

    private static final String START_DATE = "14daysAgo";
    private static final String END_DATE = "7daysAgo";
    private final static UserSteps user = new UserSteps();

    private static List<String> requiredDimensionNames;

    @Parameter(0)
    public String dimensionName;

    @Parameter(1)
    public List<String> filterDimensionNames;

    @Parameter(2)
    public Counter counter;

    private List<String> dimensionValue;
    private String filter;

    @Parameters(name = "Счетчик: {1}, измерения: {0}")
    public static Collection createParameters() {
        return asList(new Object[][]{
                {"ym:s:regionAggregated", asList("ym:s:regionCountry", "ym:s:regionArea", "ym:s:regionCity"), SENDFLOWERS_RU},
                {"ym:s:screenResolutionWV", asList("ym:s:screenWidth", "ym:s:screenHeight"), SENDFLOWERS_RU},
                {"ym:s:regionAggregated", asList("ym:s:regionCountry", "ym:s:regionArea", "ym:s:regionCity"), AT_NEW_WEBVISOR},
                {"ym:s:screenResolutionWV", asList("ym:s:screenWidth", "ym:s:screenHeight"), AT_NEW_WEBVISOR},
        });
    }

    @BeforeClass
    public static void init() {
        requiredDimensionNames = user.onWebVisorMetadataSteps().getWebVisorDefaultVisitDimensions().getRequired();
    }

    @Before
    public void setup() {
        addTestParameter("Измерение", dimensionName);

        dimensionValue = getDimensionValue();

        filter = getFilter();

        addTestParameter("Фильтр", filter);
    }

    private String getFilter() {

        assumeThat("количество значений измерения и количество измерений в фильтре совпадают", dimensionValue,
                iterableWithSize(equalTo(filterDimensionNames.size())));

        List<Term> filterTerms = new ArrayList<>();
        for (int index = 0; index < filterDimensionNames.size(); index++) {
            String value = dimensionValue.get(index);
            String dimension = filterDimensionNames.get(index);

            Term filter = value == null
                    ? dimension(dimension).notDefined()
                    : dimension(dimension).equalTo(value);

            filterTerms.add(filter);
        }

        return with(filterTerms).extract(on(Term.class).build()).join(" AND ");
    }

    @Test
    public void visitsGridFilterComplexByRowTest() {
        VisitsGridParameters reportParameters = getReportParameters();
        reportParameters.setFilters(filter);

        WebvisorV2DataVisitsGETSchema result = user.onWebVisorSteps().getVisitsGridAndExpectSuccess(reportParameters);

        List<List<String>> dimensions = user.onResultSteps().getComplexDimensionValues(dimensionName, result);

        assertThat("значение измерения в каждой строке равно заданному", dimensions,
                both(Matchers.<List<String>>iterableWithSize(greaterThan(0)))
                        .and(everyItem(equalTo(dimensionValue))));
    }

    private VisitsGridParameters getReportParameters() {
        VisitsGridParameters reportParameters = new VisitsGridParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setDimensions(requiredDimensionNames, dimensionName);
        reportParameters.setDate1(START_DATE);
        reportParameters.setDate2(END_DATE);

        return reportParameters;
    }

    private List<String> getDimensionValue() {
        VisitsGridParameters reportParameters = getReportParameters();
        reportParameters.setLimit(1);
        reportParameters.setSort(sort().by(dimensionName).descending().build());

        WebvisorV2DataVisitsGETSchema result = user.onWebVisorSteps().getVisitsGridAndExpectSuccess(reportParameters);

        assumeThat("запрос вернул ровно одну строку", result,
                having(on(WebvisorV2DataVisitsGETSchema.class).getData(), iterableWithSize(1)));

        return user.onResultSteps().getComplexDimensionValues(dimensionName, result).get(0);
    }
}
