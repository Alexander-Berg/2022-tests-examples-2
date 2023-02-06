package ru.yandex.autotests.metrika.tests.ft.report.metrika.topkeys.boundary;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

/**
 * Created by okunev on 29.10.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.TOP_KEYS})
@Title("Ограничение количества строк: проверка граничных значений")
public class TopKeysBoundaryTest {

    private static final String METRIC = "ym:s:users";
    private static final String DIMENSION = "ym:s:startURL";
    private static final int TOP_KEYS_MINIMUM = 0;
    private static final int TOP_KEYS_MAXIMUM = 100;

    private static UserSteps user;
    private static final Counter counter = CounterConstants.NO_DATA;

    private BytimeReportParameters reportParameters;

    @BeforeClass
    public static void beforeClass() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void before() {
        reportParameters = new BytimeReportParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setMetric(METRIC);
        reportParameters.setDimension(DIMENSION);
    }

    @Test
    public void bytimeTopkeysCheckMinimumPositive() {
        reportParameters.setTopKeys(TOP_KEYS_MINIMUM);

        user.onReportSteps().getBytimeReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void bytimeTopkeysCheckMaximumPositive() {
        reportParameters.setTopKeys(TOP_KEYS_MAXIMUM);

        user.onReportSteps().getBytimeReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void bytimeTopkeysCheckMinimumNegative() {
        reportParameters.setTopKeys(TOP_KEYS_MINIMUM - 1);

        user.onReportSteps().getBytimeReportAndExpectError(ReportError.MUST_BE_GREATER_THAN_OR_EQUAL_TO_ZERO,
                reportParameters);
    }

    @Test
    public void bytimeTopkeysCheckMaximumNegative() {
        reportParameters.setTopKeys(TOP_KEYS_MAXIMUM + 1);

        user.onReportSteps().getBytimeReportAndExpectError(
                ReportError.TOO_MANY_KEYS_IN_ROW_IDS, reportParameters);
    }

}
