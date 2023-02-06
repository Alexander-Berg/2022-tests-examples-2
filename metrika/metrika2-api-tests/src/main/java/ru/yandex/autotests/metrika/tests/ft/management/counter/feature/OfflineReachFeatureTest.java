package ru.yandex.autotests.metrika.tests.ft.management.counter.feature;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Счетчик: проверка фичи offline_reach")
public class OfflineReachFeatureTest {

    private UserSteps user;
    private Long counterId;

    @Before
    public void init() {
        user = new UserSteps();

        CounterFull counter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter());

        counterId = counter.getId();

        assumeThat("на счетчике нет фичи offline_reach", counter.getFeatures(), not(hasItem(Feature.OFFLINE_REACH)));
    }

    @Test
    public void checkFeatureAdd() {
        user.onManagementSteps().onCountersSteps().enableOffliReachFeature(counterId);

        CounterFull counter = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(counterId);

        assertThat("на счетчике появилась фича offline_calls", counter.getFeatures(), hasItem(Feature.OFFLINE_REACH));
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
