package ru.yandex.autotests.metrika.tests.ft.report.metrika.metrics.boundary;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.VISITS;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by konkov on 20.08.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.METRICS})
@Title("Тесты на граничные количества метрик")
public class MetricBoundaryTest {

    private static final Counter counter = CounterConstants.NO_DATA;

    /**
     * Лимит на количество метрик в запросе.
     * Источник - jkee@
     * Будет в документации: METR-12334
     */
    public static final int METRICS_LIMIT = 20;

    private static UserSteps user;

    private static Collection<String> metrics;
    private static String dimension;

    private TableReportParameters reportParameters;

    @BeforeClass
    public static void prepare() {
        user = new UserSteps().withDefaultAccuracy();

        //отбираем только непараметризованные метрики,
        // исключаем метрику, которая требует наличия особого измерения
        // и метрики, из-за которой падает запрос в кликхаус METR-20063 (метрики будут пополняться)
        metrics = user.onMetadataSteps().getMetrics(
                table(VISITS).and(nonParameterized()).and(matches(not(isIn(
                        toArray(
                                "ym:s:affinityIndexInterests",
                                "ym:s:affinityIndexInterests2",
                                "ym:s:blockedPercentage",
                                "ym:s:YACLIDPercentage",
                                "ym:s:YDCLIDPercentage",
                                "ym:s:YCLIDPercentage",
                                "ym:s:pvlAll1Window",
                                "ym:s:pvlAll3Window",
                                "ym:s:pvlAll7Window",
                                "ym:s:pvlAll<offline_window>Window",
                                "ym:s:pvl<offline_region>Region<offline_window>Window",
                                "ym:s:pvl<offline_point>Point<offline_window>Window"
                        ))))).and(matches(not(containsString(":cdp")))));
        assumeThat("для теста доступен список метрик", metrics, not(empty()));

        dimension = user.onMetadataSteps().getDimensions(table(VISITS).and(nonParameterized())).stream()
                .findFirst().get();
    }

    @Before
    public void createReportTestCase() {
        reportParameters = new TableReportParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setDimension(dimension);
    }

    @Test
    @Title("Проверка отсутствия метрик в запросе")
    public void noMetrics() {
        reportParameters.setMetric("");

        user.onReportSteps().getTableReportAndExpectError(
                400L, "Wrong parameter: 'metrics', value: ''", reportParameters);
    }

    @Test
    @Title("Проверка превышения максимального количества метрик в запросе")
    public void moreThanMaximumMetrics() {
        reportParameters.setMetrics(metrics.stream().limit(METRICS_LIMIT + 1).collect(toList()));

        user.onReportSteps().getTableReportAndExpectError(ReportError.TOO_MANY_METRICS, reportParameters);
    }

    @Test
    @Title("Проверка максимального количества метрик в запросе")
    public void maximumMetrics() {
        reportParameters.setMetrics(metrics.stream().limit(METRICS_LIMIT).collect(toList()));

        StatV1DataGETSchema result = user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);

        assertThat("результат содержит максимальное количество метрик", result,
                having(on(StatV1DataGETSchema.class).getQuery().getMetrics(), iterableWithSize(METRICS_LIMIT)));
    }
}
