package ru.yandex.autotests.metrika.tests.b2b.chartannotation;

import org.junit.Before;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;
import ru.yandex.metrika.api.management.client.external.chartannotation.ChartAnnotationGroup;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.LAMODA_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SHATURA_COM;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.BY_TIME;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.CHART_ANNOTATIONS})
@Title("B2B - примечания на графиках")
public class B2bChartAnnotationTest extends BaseB2bTest {

    private static final String METRIC = "ym:s:visits";
    private static final String DIMENSION = "ym:s:browser";

    @Parameterized.Parameters(name = "Группа примечаний: {0}, счетчик: {1}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray(ChartAnnotationGroup.MONITORING, LAMODA_RU, "2017-03-01", "2017-07-31"),
                toArray(ChartAnnotationGroup.MONITORING, SHATURA_COM, "2016-10-01", "2017-09-01"),
                toArray(ChartAnnotationGroup.HOLIDAY, LAMODA_RU, "2017-01-01", "2017-03-31")
        );
    }

    @Parameterized.Parameter
    public ChartAnnotationGroup annotationGroup;

    @Parameterized.Parameter(1)
    public Counter counter;

    @Parameterized.Parameter(2)
    public String startDate;

    @Parameterized.Parameter(3)
    public String endDate;

    @Before
    public void setup() {
        requestType = BY_TIME;
        reportParameters = new BytimeReportParameters()
                .withId(counter)
                .withDate1(startDate)
                .withDate2(endDate)
                .withMetric(METRIC)
                .withDimension(DIMENSION)
                .withIncludeAnnotations(true)
                .withAnnotationGroups(of(annotationGroup));
    }
}
