package ru.yandex.autotests.metrika.tests.ft.management.offlineconversion;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionUploadingData;
import ru.yandex.autotests.metrika.data.parameters.management.v1.OfflineConversionParameters;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.OfflineOptions;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType.BASIC;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType.CALLS;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Field.OFFLINE_OPTIONS;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createBaseData;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType.CLIENT_ID;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.OFFLINE_CONVERSION)
@Title("Включение увеличенного периода учета конверсий")
@RunWith(Parameterized.class)
public class OfflineConversionThresholdEnableTest<T extends OfflineConversionUploadingData> {

    private static UserSteps user = new UserSteps();

    private Long counterId;

    @Parameterized.Parameter
    public OfflineConversionType<T> type;

    @Parameterized.Parameter(1)
    public OfflineOptions expectedOptions;

    @Parameterized.Parameters(name = "Тип {0}")
    public static Collection<Object[]> getParameters() {
        return asList(new Object[][] {
                {
                        BASIC,
                        new OfflineOptions().withOfflineConversionExtendedThreshold(1L)
                },
                {
                        CALLS,
                        new OfflineOptions().withOfflineCallsExtendedThreshold(1L)
                }
        });
    }

    @Before
    public void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Test
    public void check() {
        user.onManagementSteps().onOfflineConversionSteps()
                .enableExtendedThreshold(type, counterId);

        CounterFull counter = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(counterId, OFFLINE_OPTIONS);

        assertThat("увеличенный период учета конверсий включен",
                counter.getOfflineOptions(),
                beanEquivalent(expectedOptions)
        );
    }

    @Test
    public void checkAfterUpload() {
        user.onManagementSteps().onOfflineConversionSteps().upload(
                type,
                counterId,
                createBaseData(type, CLIENT_ID),
                BASIC.equals(type) ?
                        new OfflineConversionParameters().withClientIdType(CLIENT_ID).withIgnoreVisitJoinThreshold(1) :
                        new OfflineConversionParameters().withClientIdType(CLIENT_ID).withIgnoreCallsVisitJoinThreshold(1)
        );

        CounterFull counter = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(counterId, OFFLINE_OPTIONS);

        assertThat("увеличенный период учета конверсий включен",
                counter.getOfflineOptions(),
                beanEquivalent(expectedOptions)
        );
    }

    @Test
    public void checkUploadUnavailable() {
        user.onManagementSteps().onOfflineConversionSteps().uploadAndExpectError(
                type,
                counterId,
                createBaseData(type, CLIENT_ID),
                ManagementError.VISIT_JOIN_THRESHOLD_UNMET,
                new OfflineConversionParameters().withClientIdType(CLIENT_ID)
        );
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
