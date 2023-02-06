package ru.yandex.autotests.metrika.tests.ft.report.metrika.dimensions;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.favorite;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;

/**
 * Created by sourx on 15.08.16.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Parameter.DIMENSIONS)
@Title("Отчет по измерениям с метрикой c параметром")
@RunWith(Parameterized.class)
public class DimensionsWithParamMetricTest {
    private static UserSteps user = new UserSteps().withDefaultAccuracy();

    private final static String METRIC = "ym:s:sumParams";
    private final static String PARAM_DIMENSION = "ym:s:paramsLevel2";
    private static final Counter COUNTER = CounterConstants.LITE_DATA;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public String dimension;

    @Parameterized.Parameters(name = "{0} {1}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(TABLE, DRILLDOWN, COMPARISON, COMPARISON_DRILLDOWN, BY_TIME)
                .values(user.onMetadataSteps().getDimensions(favorite().and(table(TableEnum.VISITS))))
                .build();
    }

    @Test
    public void check() {
        user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                new TableReportParameters()
                        .withId(COUNTER)
                        .withMetric(METRIC)
                        .withDimensions(asList(PARAM_DIMENSION, dimension)));
    }
}
