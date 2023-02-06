package ru.yandex.autotests.metrika.tests.b2b;

import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;

import static ru.yandex.autotests.metrika.data.common.counters.Counters.ECOMMERCE_TEST;

/**
 * Created by konkov on 28.09.2015.
 */
public abstract class BaseB2bEcommerceTest extends BaseB2bTest {
    protected static final Counter COUNTER = ECOMMERCE_TEST;

    protected static final String START_DATE = DateConstants.Ecommerce.START_DATE;
    protected static final String END_DATE = DateConstants.Ecommerce.END_DATE;

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeNotEmptyBoth(testingBean, referenceBean);
    }
}
