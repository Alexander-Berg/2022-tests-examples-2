package ru.yandex.autotests.internalapid.tests;

import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.internalapid.util.DataUtil;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.util.wrappers.CdpGoalsWrapper;
import ru.yandex.qatools.allure.annotations.Title;

@Title("Тесты ручек CDP целей")
public class CdpGoalsTest  extends InternalApidTest {

    private static CounterFull COUNTER;

    @BeforeClass
    public static void init() {
        COUNTER = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test.ru"));
    }

    @Test
    @Title("Тест ручки /cdp_goals")
    public void cdpGoals() {
        long counterId = COUNTER.getId();

        CdpGoalsWrapper cdpGoals = userSteps.onCdpGoalsSteps().getCdpGoalsAndExpectSuccess(counterId);

        Assert.assertNotNull("cdp order in progress цель создалась", cdpGoals.getCdpOrderInProgressGoalId());
        Assert.assertNotNull("cdp order paid цель создалась", cdpGoals.getCdpOrderPaidGoalId());
    }
}
