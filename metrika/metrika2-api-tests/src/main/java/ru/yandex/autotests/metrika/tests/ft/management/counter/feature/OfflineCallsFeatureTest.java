package ru.yandex.autotests.metrika.tests.ft.management.counter.feature;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData;
import ru.yandex.autotests.metrika.data.parameters.management.v1.OfflineConversionParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType.CALLS;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createBaseData;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;
import static ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType.CLIENT_ID;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Счетчик: проверка фичи offline_calls")
public class OfflineCallsFeatureTest {

    private static final List<CallsOfflineConversionUploadingData> DATA = createBaseData(CALLS, CLIENT_ID);

    private UserSteps user;
    private Long counterId;

    @Before
    public void init() {
        user = new UserSteps();

        CounterFull counter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter());

        counterId = counter.getId();

        assumeThat("на счетчике нет фичи offline_calls", counter.getFeatures(), not(hasItem(Feature.OFFLINE_CALLS)));
    }

    @Test
    public void checkFeatureAdd() {
        user.onManagementSteps().onOfflineConversionSteps()
                .upload(CALLS, counterId, DATA, new OfflineConversionParameters().withClientIdType(CLIENT_ID).withIgnoreCallsVisitJoinThreshold(1));

        CounterFull counter = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(counterId);

        assertThat("на счетчике появилась фича offline_calls", counter.getFeatures(), hasItem(Feature.OFFLINE_CALLS));
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
