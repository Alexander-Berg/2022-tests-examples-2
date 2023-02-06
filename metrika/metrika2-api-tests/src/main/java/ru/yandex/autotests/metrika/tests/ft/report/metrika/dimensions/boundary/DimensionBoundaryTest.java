package ru.yandex.autotests.metrika.tests.ft.report.metrika.dimensions.boundary;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
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
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.nonParameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 14.08.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.DIMENSIONS})
@Title("Тесты на граничные количества измерений")
public class DimensionBoundaryTest {

    private static final Counter counter = CounterConstants.NO_DATA;

    /**
     * Лимит на количество измерений в запросе.
     * Источник - jkee@
     * Будет в документации: METR-12334
     */
    public static final int KEYS_LIMIT = 10;

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static String metric;
    private static Collection<String> dimensions;

    private TableReportParameters reportParameters;

    @BeforeClass
    public static void init() {
        metric = user.onMetadataSteps().getMetrics(table(TableEnum.VISITS).and(nonParameterized()))
                .stream().findFirst().get();
        dimensions = user.onMetadataSteps().getDimensions(table(TableEnum.VISITS).and(nonParameterized()).and(d -> !d.startsWith("ym:s:RW")));
    }

    @Before
    public void setup() {
        reportParameters = new TableReportParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setMetric(metric);
    }

    @Test
    @Title("Проверка отсутствия измерений в запросе")
    public void noDimensions() {
        reportParameters.setDimension("");

        user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
    }

    @Test
    @Title("Проверка максимального количества измерений в запросе")
    public void maximumDimensions() {
        reportParameters.setDimensions(dimensions.stream().limit(KEYS_LIMIT).collect(toList()));

        StatV1DataGETSchema result = user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);

        assertThat("ответ содежит максимальное количество измерений", result,
                having(on(StatV1DataGETSchema.class).getQuery().getDimensions(),
                        iterableWithSize(KEYS_LIMIT)));
    }

    @Test
    @Title("Проверка превышения максимального количества измерений в запросе")
    public void moreThanMaximumDimensions() {
        reportParameters.setDimensions(dimensions.stream().limit(KEYS_LIMIT + 1).collect(toList()));

        user.onReportSteps().getTableReportAndExpectError(ReportError.TOO_MANY_DIMENSIONS, reportParameters);
    }
}
