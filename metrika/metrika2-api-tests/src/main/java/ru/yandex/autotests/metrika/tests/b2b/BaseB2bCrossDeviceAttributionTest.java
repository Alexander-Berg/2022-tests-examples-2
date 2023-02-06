package ru.yandex.autotests.metrika.tests.b2b;

import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;

import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;

public class BaseB2bCrossDeviceAttributionTest extends BaseB2bTest {

    protected static final Counter COUNTER = YANDEX_METRIKA_2_0;

    protected static final String START_DATE = DateConstants.CrossDeviceAttribution.START_DATE;
    protected static final String END_DATE = DateConstants.CrossDeviceAttribution.END_DATE;

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeNotEmptyBoth(testingBean, referenceBean);
    }
}
