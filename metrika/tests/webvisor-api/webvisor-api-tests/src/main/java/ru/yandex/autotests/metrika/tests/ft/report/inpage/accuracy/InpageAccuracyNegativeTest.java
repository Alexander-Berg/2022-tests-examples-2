package ru.yandex.autotests.metrika.tests.ft.report.inpage.accuracy;

import java.util.Collection;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.inpage.v1.InpageDataParameters;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.INPAGE_CLICK;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.INPAGE_FORM;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.INPAGE_LINK;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.INPAGE_SCROLL;

/**
 * Created by sonick on 21.11.16.
 */
@Features(Requirements.Feature.INPAGE)
@Stories( Requirements.Story.Report.Parameter.ACCURACY)
@Title("Inpage: негативные тесты на параметр accuracy")
@RunWith(Parameterized.class)
public class InpageAccuracyNegativeTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    protected static final String START_DATE = "14daysAgo";
    protected static final String END_DATE = "7daysAgo";

    protected static final int HEIGHT = 100;
    protected static final String URL = "https://news.yandex.ru/";
    protected static final String LINKURL = "https://news.yandex.ru/politics.html";

    protected static Counter COUNTER = CounterConstants.NO_DATA;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    @Parameterized.Parameter(2)
    public String accuracy;

    @Parameterized.Parameters(name = "{0} \"{2}\"")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(INPAGE_CLICK, new InpageDataParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withHeight(String.valueOf(HEIGHT))
                                .withUrl(URL)),
                        of(INPAGE_FORM, new InpageDataParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withUrl(URL)),
                        of(INPAGE_SCROLL, new InpageDataParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withHeight(String.valueOf(HEIGHT))
                                .withUrl(URL)),
                        of(INPAGE_LINK, new InpageDataParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withUrl(LINKURL)))
                .values(of(" ", "1.1", "2", "0", "-1", "Z", "Я", "\u1000", "very long string"))
                .build();
    }

    @Test
    public void accuracyNegativeTest() {
        user.onInpageSteps().getInpageReportAndExpectError(requestType, ReportError.WRONG_ACCURACY_FORMAT,
                parameters,
                new InpageDataParameters()
                        .withId(COUNTER)
                        .withAccuracy(accuracy));
    }
}
