package ru.yandex.autotests.metrika.tests.ft.report.metrika.callback;

import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SHATURA_COM;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;

/**
 * Created by konkov on 20.02.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.CALLBACK})
@Title("Отчет 'таблица': callback негативные")
@RunWith(Parameterized.class)
public class TableCallbackNegativeTest {

    private static UserSteps user;
    private static final Counter counter = SHATURA_COM;

    private static final String DIMENSION_NAME = "ym:s:gender";
    private static final String METRIC_NAME = "ym:s:visits";

    private static final String START_DATE = "2015-01-31";
    private static final String END_DATE = "2015-01-31";

    private static final String CALLBACK_FUNCTION = "abc()-def";

    @Parameter()
    public String title;

    @Parameter(1)
    public IFormParameters requestParameters;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {"Успешный ответ", getReportParameters(true)},
                {"Ошибочный ответ", getReportParameters(false)}
        });
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Test
    public void checkCallbackFunction() {
        StatV1DataGETSchema ignore = user.onReportSteps().getTableReportAndExpectError(ReportError.INVALID_PARAMETER,
                requestParameters,
                makeParameters("callback", CALLBACK_FUNCTION));
    }

    private static IFormParameters getReportParameters(boolean isGood) {
        TableReportParameters reportParameters = new TableReportParameters();

        reportParameters.setId(counter.get(ID));
        reportParameters.setDimension(DIMENSION_NAME);
        if (isGood) {
            reportParameters.setMetric(METRIC_NAME);
        }
        reportParameters.setDate1(START_DATE);
        reportParameters.setDate2(END_DATE);

        return reportParameters;
    }
}
