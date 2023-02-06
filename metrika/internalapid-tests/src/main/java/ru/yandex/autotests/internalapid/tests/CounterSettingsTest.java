package ru.yandex.autotests.internalapid.tests;


import org.hamcrest.Matcher;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.internalapid.util.DataUtil;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterStatus;
import ru.yandex.metrika.api.management.client.external.CounterType;
import ru.yandex.metrika.internalapid.common.CounterSettings;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasProperty;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Title("Тест ручки /counter_settings")
public class CounterSettingsTest extends InternalApidTest {
    private static CounterFull COUNTER;
    private static final String SITE = "counter.settings.test.ru";


    @BeforeClass
    public static void init() {
        COUNTER = userSteps.onInternalApidSteps().createCounter(new CounterFull()
                .withSite(SITE)
                .withName(DataUtil.getRandomCounterName())
                .withAutogoalsEnabled(true)
                .withGdprAgreementAccepted(1L) //true
                .withStatus(CounterStatus.ACTIVE)
                .withType(CounterType.SIMPLE));
    }

    @Test
    public void testCounterSettings() {
        CounterSettings counterSettings = userSteps.onCountersSteps().getCounterSettings(COUNTER.getId());

        assertThat("Настройки счетчика совпадают",
                counterSettings,
                matchCounterSettings());
    }


    private Matcher<CounterSettings> matchCounterSettings() {
        return allOf(
                hasProperty("counterId", equalTo(COUNTER.getId())),
                hasProperty("autoGoalsEnabled", equalTo(COUNTER.getAutogoalsEnabled())),
                hasProperty("gdprAgreementAccepted", equalTo(getBooleanFromLong(COUNTER.getGdprAgreementAccepted()))),
                hasProperty("status", equalTo(COUNTER.getStatus())),
                hasProperty("type", equalTo(COUNTER.getType()))
        );
    }

    private static boolean getBooleanFromLong(Long b) {
        return b != null && b != 0;
    }

}
