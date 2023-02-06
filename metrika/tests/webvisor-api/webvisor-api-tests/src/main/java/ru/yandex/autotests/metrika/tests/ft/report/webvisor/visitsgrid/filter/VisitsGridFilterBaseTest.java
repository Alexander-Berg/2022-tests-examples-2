package ru.yandex.autotests.metrika.tests.ft.report.webvisor.visitsgrid.filter;

import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataVisitsGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.VisitsGridParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;

import java.util.List;
import java.util.stream.Collectors;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.Matchers.*;
import static org.hamcrest.core.Every.everyItem;
import static org.junit.runners.Parameterized.Parameter;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.AT_NEW_WEBVISOR;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
import static ru.yandex.autotests.metrika.utils.AllureUtils.*;

/**
 * Created by konkov on 25.12.2014.
 */
public abstract class VisitsGridFilterBaseTest {

    protected static final List<Counter> COUNTERS = of(SENDFLOWERS_RU, AT_NEW_WEBVISOR);

    protected static final String START_DATE = "14daysAgo";
    protected static final String END_DATE = "7daysAgo";

    protected final static UserSteps user = new UserSteps();

    protected static List<String> requiredDimensionNames;

    @Parameter()
    public String dimensionName;

    @Parameter(1)
    public Counter counter;

    protected String dimensionValue;
    protected String filter;

    @BeforeClass
    public static void init() {
        requiredDimensionNames = user.onWebVisorMetadataSteps().getWebVisorDefaultVisitDimensions().getRequired();
    }

    @Before
    public void setup() {
        addTestParameter("Измерение", dimensionName);

        dimensionValue = getDimensionValue(dimensionName);

        filter = getFilter();

        addTestParameter("Фильтр", filter);
    }

    @Test
    public void visitsGridFilterByRowTest() {
        VisitsGridParameters reportParameters = getReportParameters();
        reportParameters.setFilters(filter);

        WebvisorV2DataVisitsGETSchema result = user.onWebVisorSteps().getVisitsGridAndExpectSuccess(reportParameters);

        List<String> dimensionValues = user.onResultSteps().getDimensionValues(dimensionName, result);
        List<String> dimensions = dimensionValues.stream().map(d -> removeSlash(d)).collect(Collectors.toList());

        assertThat("значение измерения в каждой строке равно заданному", dimensions,
                both(Matchers.<String>iterableWithSize(greaterThan(0)))
                        .and(everyItem(equalTo(removeSlash(dimensionValue)))));
    }

    private String getDimensionValue(String dimensionName) {
        VisitsGridParameters reportParameters = getReportParameters();
        reportParameters.setLimit(1);
        reportParameters.setSort(sort().by(dimensionName).descending().build());

        WebvisorV2DataVisitsGETSchema result = user.onWebVisorSteps().getVisitsGridAndExpectSuccess(reportParameters);

        assumeThat("запрос вернул ровно одну строку", result,
                having(on(WebvisorV2DataVisitsGETSchema.class).getData(), iterableWithSize(1)));

        return user.onResultSteps().getDimensionValues(dimensionName, result).get(0);
    }

    private String removeSlash(String dimensionValue) {
        if (dimensionValue != null && dimensionValue.endsWith("/") && dimensionValue.startsWith("http")) {
            return dimensionValue.replaceAll("/$", "");
        } else {
            return dimensionValue;
        }
    }

    private VisitsGridParameters getReportParameters() {
        VisitsGridParameters reportParameters = new VisitsGridParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setDimensions(requiredDimensionNames, dimensionName);
        reportParameters.setDate1(START_DATE);
        reportParameters.setDate2(END_DATE);

        return reportParameters;
    }

    private String getFilter() {
        return dimensionValue == null
                ? dimension(dimensionName).notDefined().build()
                : dimension(dimensionName).equalTo(dimensionValue).build();
    }
}
