package ru.yandex.autotests.metrika.tests.b2b.inpage;

import java.util.Collection;

import org.junit.Before;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.inpage.v1.InpageDataParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.apache.commons.lang3.StringEscapeUtils.escapeJava;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.INOPTIKA_RU;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.INPAGE_FORM;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by konkov on 13.08.2015.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Inpage.FORM})
@Title("B2B - In-page аналитика: аналитика форм")
public class B2bInpageFormTest extends BaseB2bTest {

    private static final Counter COUNTER = INOPTIKA_RU;
    private static final String DATE1 = "14daysAgo";
    private static final String DATE2 = "7daysAgo";

    private static final String METRIC = "ym:pv:pageviews";
    private static final String DIMENSION = "ym:pv:URLHash";

    @Parameter()
    public String url;

    @Parameter(1)
    public String title;

    @Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        StatV1DataGETSchema result = userOnTest.onReportFacedSteps()
                .getTableReportAndExpectSuccess(new TableReportParameters()
                        .withId(COUNTER.get(ID))
                        .withDate1(DATE1)
                        .withDate2(DATE2)
                        .withMetric(METRIC)
                        .withDimension(DIMENSION));

        assumeThat("для теста доступен список адресов", result.getData(), is(not(empty())));

        return userOnTest.onResultSteps().getDimensionNameOnly(DIMENSION, result).stream()
                .map(u -> toArray(u, escapeJava(u)))
                .collect(toList());
    }

    @Before
    public void setup() {
        requestType = INPAGE_FORM;

        reportParameters = new InpageDataParameters()
                .withId(COUNTER.get(ID))
                .withUrl(url)
                .withDate1(DATE1)
                .withDate2(DATE2);
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
    }
}
