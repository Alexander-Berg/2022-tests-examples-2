package ru.yandex.autotests.metrika.tests.b2b.inpage;

import java.util.Arrays;
import java.util.Collection;

import org.junit.Before;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.inpage.v1.InpageUrlsParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.INOPTIKA_RU;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.INPAGE_LINK_URLS;

/**
 * Created by konkov on 13.08.2015.
 */
@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.Inpage.SCROLL,
        Requirements.Story.Inpage.FORM,
        Requirements.Story.Inpage.LINK,
        Requirements.Story.Inpage.CLICK
})
@Title("B2B - In-page аналитика: списки URL'ов")
public class B2bInpageUrlsTest extends BaseB2bTest {

    private static final Counter COUNTER = INOPTIKA_RU;
    private static final String DATE1 = "14daysAgo";
    private static final String DATE2 = "7daysAgo";


    @Parameter()
    public RequestType<?> requestType;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return Arrays.<Object[]>asList(
                toArray(INPAGE_LINK_URLS));
    }

    @Before
    public void setup() {
        super.requestType = requestType;

        reportParameters = new InpageUrlsParameters()
                .withId(COUNTER.get(ID))
                .withDate1(DATE1)
                .withDate2(DATE2);
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
    }
}
