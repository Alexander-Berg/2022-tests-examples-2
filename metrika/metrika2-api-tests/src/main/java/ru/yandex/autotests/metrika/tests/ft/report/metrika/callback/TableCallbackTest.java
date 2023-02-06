package ru.yandex.autotests.metrika.tests.ft.report.metrika.callback;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.StringUtils.substringBetween;
import static org.hamcrest.Matchers.*;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints.ignore;
import static ru.yandex.autotests.metrika.core.MetrikaJson.GSON_RESPONSE;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SHATURA_COM;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.TABLE;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 20.02.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.CALLBACK})
@Title("Отчет 'таблица': callback")
@RunWith(Parameterized.class)
public class TableCallbackTest {

    private static UserSteps user;
    private static final Counter counter = SHATURA_COM;

    private static final String DIMENSION_NAME = "ym:s:gender";
    private static final String METRIC_NAME = "ym:s:visits";

    private static final String START_DATE = "2015-01-31";
    private static final String END_DATE = "2015-01-31";

    private static final String CALLBACK_FUNCTION = "jscallback";
    private static final String JAVA_SCRIPT_PREFIX = "/**/try{"+ CALLBACK_FUNCTION + "(";
    private static final String JAVA_SCRIPT_SUFFIX = ");}catch(e){}";

    private String javaScriptResponse;
    private Object result;
    private Object resultFromJavaScript;

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

    @Before
    public void setup() {
        javaScriptResponse = user.onReportSteps().getTableReport(CALLBACK_FUNCTION, requestParameters);
        result = user.onReportSteps().getRawReport(TABLE, requestParameters);
        resultFromJavaScript = parseJavaScript(javaScriptResponse);
    }

    private Object parseJavaScript(String javaScriptResponse) {
        String jsonResponse = substringBetween(javaScriptResponse, JAVA_SCRIPT_PREFIX, JAVA_SCRIPT_SUFFIX);
        return GSON_RESPONSE.fromJson(jsonResponse, StatV1DataGETSchema.class);
    }

    @Test
    public void checkCallbackFunction() {
        assertThat("ответ содержит функцию-callback",
                javaScriptResponse,
                both(startsWith(JAVA_SCRIPT_PREFIX)).and(endsWith(JAVA_SCRIPT_SUFFIX)));
    }

    @Test
    public void checkCallbackArgument() {
        assertThat("ответ содержит результат запроса отчета",
                result, beanEquivalent(resultFromJavaScript)
                        .fields(ignore("dataLag", "profile", "sampleSize", "sampleSpace")));
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
