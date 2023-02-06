package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.bytime;

import java.util.Arrays;
import java.util.Collection;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;

@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет 'по времени': на отобранных вручную параметрах запросов ByTime")
@RunWith(Parameterized.class)
public class ParticularsByTimeTest {
    protected static final UserSteps userOnTest = new UserSteps().withDefaultAccuracy();

    @Parameterized.Parameter()
    public IFormParameters reportParameters;

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return Arrays.<Object[]>asList(
                new Object[]{new BytimeReportParameters()
                        .withId(SENDFLOWERS_RU)
                        .withDate1("2020-10-05")
                        .withDate2("2021-06-13")
                        .withDimensions(Arrays.asList("ym:s:date", "ym:s:hourMinute", "ym:s:firstSourceEngine", "ym:s:isNewUser"))
                        .withFilters("ym:s:date!n")
                        .withRowIds("[[\"2021-03-30\",\"16:48\",\"ad.Google Ads\",\"yes\"],[\"2021-03-30\",\"16:50\",\"ad" +
                        ".Google Ads\",\"yes\"],[\"2021-03-30\",\"16:57\",\"ad.Google Ads\",\"yes\"],[\"2021-03-30\"," +
                        "\"16:55\",\"ad.Google Ads\",\"yes\"],[\"2021-03-30\",\"17:00\",\"ad.Google Ads\",\"yes\"]]")
                        .withMetric("ym:s:visits")
                }
        );
    }

    @Test
    public void check() {
        userOnTest.onReportSteps().getReportAndExpectSuccess(RequestTypes.BY_TIME, reportParameters);
    }
}
