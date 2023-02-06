package ru.yandex.autotests.metrika.tests.b2b;

import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;

import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_NEWS;

public class BaseB2bYanTest extends BaseB2bTest {
    protected static final Counter COUNTER = YANDEX_NEWS;

    protected static final String START_DATE = DateConstants.Yan.START_DATE;
    protected static final String END_DATE = DateConstants.Yan.END_DATE;

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeNotEmptyBoth(testingBean, referenceBean);
    }
}
