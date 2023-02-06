package ru.yandex.autotests.metrika.tests.ft.report.metrika.presets.overriding;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.lang.String.format;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.matchers.SortMatcher.isSortEqualTo;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by konkov on 04.09.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.PRESET})
@Title("Перекрытие параметров шаблона")
public class OverridingTest {

    private static final Counter counter = CounterConstants.NO_DATA;
    private static final String PRESET = "tech_browsers";
    private static final List<String> METRICS = asList("ym:s:users", "ym:s:cookieEnabledPercentage");
    private static final String SORT_FOR_METRICS = sort().by("ym:s:users").descending().build();
    private static final String DIMENSION = "ym:s:operatingSystem";
    private static final String SORT = sort().by("ym:s:pageDepth").descending().build();

    private static UserSteps user;

    private TableReportParameters reportParameters;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new TableReportParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setPreset(PRESET);
    }

    @Test
    public void overrideMetric() {
        reportParameters.setMetrics(METRICS);
        reportParameters.setSort(SORT_FOR_METRICS);

        StatV1DataGETSchema result = user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
        assumeThat("результат содержит исходный запрос", result,
                having(on(StatV1DataGETSchema.class).getQuery(), notNullValue()));

        assertThat("результат содержит наименование метрики", result,
                having(on(StatV1DataGETSchema.class).getQuery().getMetrics(), equalTo(METRICS)));
    }

    @Test
    public void overrideDimension() {
        reportParameters.setDimension(DIMENSION);

        StatV1DataGETSchema result = user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
        assumeThat("результат содержит исходный запрос", result,
                having(on(StatV1DataGETSchema.class).getQuery(), notNullValue()));

        assertThat("результат содержит наименование измерения", result,
                having(on(StatV1DataGETSchema.class).getQuery().getDimensions(), hasItem(DIMENSION)));
    }

    @Test
    public void overrideSort() {
        reportParameters.setSort(SORT);

        StatV1DataGETSchema result = user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
        assumeThat("результат содержит исходный запрос", result,
                having(on(StatV1DataGETSchema.class).getQuery(), notNullValue()));

        assertThat(format("результат содержит сортировку %s", SORT), result,
                having(on(StatV1DataGETSchema.class).getQuery().getSort(), isSortEqualTo(SORT)));
    }
}
