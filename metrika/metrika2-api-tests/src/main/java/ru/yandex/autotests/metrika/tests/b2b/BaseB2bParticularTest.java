package ru.yandex.autotests.metrika.tests.b2b;

import org.junit.Before;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.data.b2b.B2bSample;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.changeTestCaseTitle;

/**
 * Created by konkov on 30.09.2015.
 */
public abstract class BaseB2bParticularTest extends BaseB2bTest {

    @Parameterized.Parameter()
    public B2bSample sample;

    @Before
    public void setup() {
        super.requestType = sample.getRequestType();
        super.reportParameters = sample.getParameters();
        changeTestCaseTitle(sample.getTitle());
    }

    protected static Object[] createParams(String title, RequestType<?> requestType, IFormParameters... params) {
        return toArray(new B2bSample()
                .withTitle(title)
                .withRequestType(requestType)
                .withParameters(params));
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeNotEmptyBoth(testingBean, referenceBean);
    }
}
