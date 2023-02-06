package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting;

import com.google.common.collect.ImmutableList;
import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.errors.ReportError;
import ru.yandex.autotests.metrika.appmetrica.parameters.BytimeReportParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.utils.ReportType;
import ru.yandex.autotests.metrika.appmetrica.utils.ReportTypes;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Collections;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.changeTestCaseTitle;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.appmetrica.utils.ReportTypes.*;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;

@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.DIMENSIONS)
@Title("Апи отчётов (400-ые ответы)")
@RunWith(Parameterized.class)
public class ReportNegativeTest {

    private static final UserSteps onTesting = UserSteps.builder()
            .withBaseUrl(AppMetricaApiProperties.apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    @Parameterized.Parameter()
    public String title;

    @Parameterized.Parameter(1)
    public ReportType<?> reportType;

    @Parameterized.Parameter(2)
    public IExpectedError expectedError;

    @Parameterized.Parameter(3)
    public IFormParameters parameters;

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .addAll(createParams("MOBMET-8566: json string in rowIds of bytime",
                        BYTIME, ReportError.CONVERSION_FAILED, new BytimeReportParameters()
                                .withId(Applications.YANDEX_KEYBOARD)
                                .withAccuracy("0.1")
                                .withDate1("2017-07-01")
                                .withDate2("2017-07-07")
                                .withMetrics(of("ym:u:users"))
                                .withRowIds("\"json string\"")))
                .addAll(createParams("METR-37429: many parentId parameters in drilldown",
                        DRILLDOWN, ReportError.CONVERSION_FAILED,
                        () -> ImmutableList.<NameValuePair>builder()
                                .add(new BasicNameValuePair("id", "2"))
                                .add(new BasicNameValuePair("date1", "2020-03-20"))
                                .add(new BasicNameValuePair("date2", "2020-03-20"))
                                .add(new BasicNameValuePair("dimensions", "ym:ce2:eventLabel,ym:ce2:paramsLevel1,ym:ce2:paramsLevel2"))
                                .add(new BasicNameValuePair("metrics", "ym:ce2:users"))
                                .add(new BasicNameValuePair("parentId", "[\"application.start-session\"]"))
                                .add(new BasicNameValuePair("parentId", "[\"double\"]"))
                                .build()))
                // в целом можно было бы просто пустой ответ отдавать
                .addAll(createNotRepetitiveParams("MOBMET-14722: incorrect specialDefaultDate interval",
                        TABLE, ReportError.WRONG_START_END_DATE, new TableReportParameters()
                                .withId(Applications.YANDEX_KEYBOARD)
                                .withAccuracy("0.1")
                                .withDate1("2021-06-01")
                                .withDate2("2021-06-01")
                                .withMetrics(of("ym:ts:users"))
                                .withFilters("exists ym:ce:device with (specialDefaultDate>='2021-06-01' and specialDefaultDate<='2021-05-30')")))
                .addAll(createNotRepetitiveParams("MOBMET-15241: segment attribute in segment parameter",
                        TABLE, ReportError.SEGMENT_ATTRIBUTE_NOT_ALLOWED, new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withAccuracy("0.01")
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withDimension("ym:ce2:segment")
                                .withMetrics(ImmutableList.of("ym:ce2:users,ym:ce2:eventsPerUser"))
                                .withLimit(10),
                        FreeFormParameters.makeParameters()
                                .append("segments", "" +
                                        "[\"eventLabel=='ad_requested'\", " +
                                        "\"gender=='male' and segment=='2'\"]")))
                .addAll(createNotRepetitiveParams("MOBMET-15241: segment attribute in subquery",
                        TABLE, ReportError.SEGMENT_ATTRIBUTE_NOT_ALLOWED, new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withAccuracy("0.01")
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withDimension("ym:ce2:segment")
                                .withMetrics(ImmutableList.of("ym:ce2:users,ym:ce2:eventsPerUser"))
                                .withFilters("exists ym:i:device with (campaign=='8' and segment=='1')")
                                .withLimit(10),
                        FreeFormParameters.makeParameters()
                                .append("segments", "" +
                                        "[\"eventLabel=='ad_requested'\", \"gender=='male'\"]")))
                .addAll(createNotRepetitiveParams("MOBMET-15725: no escaping for parameter in dimension",
                        TABLE, ReportError.WRONG_EXPRESSION, new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withDimension("ym:ce2:paramValue{'no escaping''}")
                                .withMetrics(ImmutableList.of("ym:ce2:users"))))
                .addAll(createNotRepetitiveParams("MOBMET-15725: missing attribute",
                        TABLE, ReportError.ERR_WRONG_ATTRIBUTE, new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withDimension("ym:ce2:paramV{'bebe'}")
                                .withMetrics(ImmutableList.of("ym:ce2:users"))))
                .addAll(createNotRepetitiveParams("MOBMET-15725: wrong attribute",
                        TABLE, ReportError.WRONG_EXPRESSION, new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withDimension("ym:ce2:paramValuea'b")
                                .withMetrics(ImmutableList.of("ym:ce2:users"))))
                .addAll(createNotRepetitiveParams("MOBMET-15725: missing attribute",
                        TABLE, ReportError.ERR_WRONG_METRIC, new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withMetrics(ImmutableList.of("ym:ce2:bebeb"))))
                .addAll(createNotRepetitiveParams("MOBMET-15725: no escaping for parameter in metric",
                        TABLE, ReportError.ERR_WRONG_METRIC, new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withMetrics(ImmutableList.of("ym:ce2:bebeb"))))
                .addAll(createNotRepetitiveParams("MOBMET-15725: no escaping for parameter in filters",
                        TABLE, ReportError.ERR_WRONG_FILTER, new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withFilters("ym:ce2:paramValue{'no escaping''}=='a'")
                                .withMetrics(ImmutableList.of("ym:ce2:users"))))
                .build();
    }

    @Before
    public void setup() {
        changeTestCaseTitle(title);
        setCurrentLayerByApp(ReportTypes.extractAppId(parameters));
    }

    @SuppressWarnings("unchecked")
    @Test
    public void check() {
        Object response = reportType.getReport(onTesting, parameters);
        assertThat(ERROR_MESSAGE, response, expectError(expectedError));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    private static List<Object[]> createParams(String title,
                                               ReportType<?> reportType,
                                               IExpectedError error,
                                               IFormParameters parameters) {
        return Collections.singletonList(toArray(title, reportType, error, parameters));
    }

    /**
     * Этот метод для повторяющихся параметров оставляет только один, поэтому подходит не для всех тестов
     */
    private static List<Object[]> createNotRepetitiveParams(String title,
                                                            ReportType<?> reportType,
                                                            IExpectedError error,
                                                            IFormParameters... parameters) {
        return Collections.singletonList(toArray(title, reportType, error, makeParameters().append(parameters)));
    }
}
