package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.data.common.CounterConstants.LITE_DATA;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by sourx on 25.01.2016.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: сегментация по рекламным системам (негативные)")
@Issue("METRIQA-304")
public class FilterNegativeAttributeAdvertisingTest {
    private static final Counter COUNTER = LITE_DATA;
    private static final String FILTER = dimension("ym:s:<attribution>AdvEngine").equalTo("1").build();
    private static final String METRIC = "ym:s:visits";
    private static final String DIMENSION = null;

    private UserSteps user = new UserSteps().withDefaultAccuracy();

    @Before
    public void setup() {
        StatV1DataGETSchema report = user.onReportSteps().getTableReportAndExpectSuccess(getReportParameters());

        assumeThat("отчет без фильтра содержит данные", report.getData(), not(empty()));
    }

    @Test
    public void reportShouldBeEmpty() {
        StatV1DataGETSchema report = user.onReportSteps().getTableReportAndExpectSuccess(getReportParameters()
                .withFilters(FILTER));

        assertThat("отчет не содержит данных", report.getData(), empty());
    }

    private TableReportParameters getReportParameters() {
        return new TableReportParameters()
                .withId(COUNTER)
                .withDimension(DIMENSION)
                .withMetric(METRIC)
                .withAccuracy("low");
    }
}

