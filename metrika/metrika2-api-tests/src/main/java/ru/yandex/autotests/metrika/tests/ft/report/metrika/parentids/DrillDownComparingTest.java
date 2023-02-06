package ru.yandex.autotests.metrika.tests.ft.report.metrika.parentids;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.beans.ReportResultInfo.from;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Parameter.PARENT_ID, Requirements.Story.Report.Type.DRILLDOWN})
@Title("Отчет Drilldown, сравнение с таблицей")
@RunWith(Parameterized.class)
public class DrillDownComparingTest {

    private static final Counter COUNTER = YANDEX_METRIKA;
    private static final String START_DATE = "2016-02-01";
    private static final String END_DATE = "2016-02-29";
    private static final String SORT = "-ym:s:visits";
    private static final int LIMIT = 50;

    private static final List<String> DEFAULT_METRICS = of(
            "ym:s:visits",
            "ym:s:users",
            "ym:s:bounceRate",
            "ym:s:pageDepth",
            "ym:s:avgVisitDurationSeconds"
    );

    // secure metrics are handled specifically by drilldown, so test it separately
    private static final String SECURE_METRIC = "ym:s:manPercentage";

    private static final List<String> DIMENSION_LEVELS = of(
            "ym:s:browser",
            "ym:s:browserAndVersionMajor",
            "ym:s:browserAndVersion"
    );

    private static final List<List<String>> DIMENSION_EXPAND_VALUES = of(
            emptyList(),
            of("6"), // Google Chrome
            of("5"), // MSIE
            of("70"), // Яндекс.Браузер
            of("4"), // Safari
            of("3"), // Firefox
            of("70", "70.14"), // Яндекс.Браузер 14
            of("4", "4.6"), // Safari 6
            of("3", "3.38") // Firefox 38
    );

    private UserSteps user;
    private TableReportParameters tableReportParameters;
    private DrillDownReportParameters drillDownReportParameters;

    @Parameter
    public Integer level;

    @Parameter(1)
    public List<String> parentIds;

    @Parameter(2)
    public List<String> additionalMetrics;

    @Parameters(name = "level={0},parentIds={1},additionalMetrics={2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(DIMENSION_EXPAND_VALUES.stream()
                        .map(strings -> of(strings.size(), strings))
                        .collect(Collectors.toList())
                )
                .values(
                        emptyList(),
                        singletonList(SECURE_METRIC)
                )
                .build();
    }

    @Before
    public void init() {
        user = new UserSteps().withDefaultAccuracy();

        List<String> metrics = Stream.concat(DEFAULT_METRICS.stream(), additionalMetrics.stream())
                .collect(Collectors.toList());

        Expression tableFilter = dimension(DIMENSION_LEVELS.get(level)).defined();
        if (level > 0) {
            tableFilter = tableFilter
                    .and(dimension(DIMENSION_LEVELS.get(level - 1)).in(parentIds.get(level - 1)));
        }

        tableReportParameters = new TableReportParameters()
                .withId(COUNTER)
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withSort(SORT)
                .withLimit(LIMIT)
                .withMetrics(metrics)
                .withFilters(tableFilter.build())
                .withDimension(DIMENSION_LEVELS.get(level));

        drillDownReportParameters = new DrillDownReportParameters()
                .withId(COUNTER.get(ID))
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withSort(SORT)
                .withLimit(LIMIT)
                .withMetrics(metrics)
                .withParentIds(parentIds)
                .withFilters(dimension(DIMENSION_LEVELS.get(level)).defined().build())
                .withDimensions(DIMENSION_LEVELS);
    }

    @Test
    public void check() {
        StatV1DataGETSchema tableResult = user.onReportSteps()
                .getTableReportAndExpectSuccess(tableReportParameters);

        StatV1DataDrilldownGETSchema drillDownResult = user.onReportSteps()
                .getDrilldownReportAndExpectSuccess(drillDownReportParameters);

        assertThat("Результат drillDown совпадает с table", from(drillDownResult),
                beanEquivalent(from(tableResult)));
    }
}
