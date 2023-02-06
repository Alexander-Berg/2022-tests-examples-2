package ru.yandex.autotests.metrika.tests.ft.management.offlineconversion;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionUploadingData;
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
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.OFFLINE_CONVERSION)
@Title("Выключение увеличенного периода период учета конверсий")
@RunWith(Parameterized.class)
public class OfflineConversionThresholdDisableTest<T extends OfflineConversionUploadingData> {

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
                        new OfflineOptions().withOfflineConversionExtendedThreshold(0L)
                },
                {
                        CALLS,
                        new OfflineOptions().withOfflineCallsExtendedThreshold(0L)
                }
        });
    }

    @Before
    public void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter().withOfflineOptions(new OfflineOptions()
                        .withOfflineConversionExtendedThreshold(1L)
                        .withOfflineCallsExtendedThreshold(1L)))
                .getId();
    }

    @Test
    public void check() {
        user.onManagementSteps().onOfflineConversionSteps()
                .disableExtendedThreshold(type, counterId);

        CounterFull counter = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(counterId, OFFLINE_OPTIONS);

        assertThat("увеличенный период учета конверсий выключен",
                counter.getOfflineOptions(),
                beanEquivalent(expectedOptions)
        );
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
