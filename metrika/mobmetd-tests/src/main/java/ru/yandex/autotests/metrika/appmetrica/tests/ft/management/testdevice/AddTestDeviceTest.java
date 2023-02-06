package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.testdevice;

import java.util.Collection;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.TestDeviceWrapper;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.TestDevice;
import ru.yandex.metrika.mobmet.model.TestDevicePurpose;
import ru.yandex.metrika.mobmet.model.TestDeviceType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.CoreMatchers.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.parameters.TestDevicePurposeParameters.param;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.testDevice;
import static ru.yandex.metrika.mobmet.model.TestDevicePurpose.PUSH_NOTIFICATIONS;
import static ru.yandex.metrika.mobmet.model.TestDevicePurpose.REATTRIBUTION;
import static ru.yandex.metrika.mobmet.model.TestDeviceType.APPMETRICA_DEVICE_ID;
import static ru.yandex.metrika.mobmet.model.TestDeviceType.GOOGLE_AID;
import static ru.yandex.metrika.mobmet.model.TestDeviceType.HUAWEI_OAID;
import static ru.yandex.metrika.mobmet.model.TestDeviceType.IOS_IFA;
import static ru.yandex.metrika.mobmet.model.TestDeviceType.IOS_IFV;
import static ru.yandex.metrika.mobmet.model.TestDeviceType.WINDOWS_AID;

/**
 * Created by graev on 18/01/2017.
 */

@Features(Requirements.Feature.Management.TEST_DEVICES)
@Stories({
        Requirements.Story.TestDevices.ADD,
        Requirements.Story.TestDevices.LIST
})
@Title("Добавление тестового устройства")
@RunWith(Parameterized.class)
public final class AddTestDeviceTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private static final UserSteps userSteps = UserSteps.onTesting(OWNER);

    @Parameterized.Parameter
    public TestDevicePurpose devicePurpose;

    @Parameterized.Parameter(1)
    public TestDeviceType deviceType;

    private TestDevice expectedDevice;

    private Long appId;

    private TestDeviceWrapper addedDevice;

    @Parameterized.Parameters(name = "Назначение={0}, Тип={1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .addAll(CombinatorialBuilder.builder()
                        .values(REATTRIBUTION, PUSH_NOTIFICATIONS)
                        .values(GOOGLE_AID, IOS_IFA, WINDOWS_AID)
                        .build())
                .add(new Object[]{PUSH_NOTIFICATIONS, APPMETRICA_DEVICE_ID})
                .add(new Object[]{PUSH_NOTIFICATIONS, IOS_IFV})
                .add(new Object[]{PUSH_NOTIFICATIONS, HUAWEI_OAID})
                .build();
    }

    @Before
    public void setup() {
        TestDeviceWrapper deviceToAdd = new TestDeviceWrapper(testDevice(devicePurpose, deviceType));
        expectedDevice = deviceToAdd.get();

        Application application = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = application.getId();

        addedDevice = new TestDeviceWrapper(userSteps.onTestDevicesSteps().createTestDevice(appId, deviceToAdd));
    }

    @Test
    public void checkDeviceInfo() {
        assertThat("добавленное тестовое устройство эквивалентно ожидаемому", addedDevice.get(),
                equivalentTo(expectedDevice));
    }

    @Test
    public void checkDeviceInList() {
        final List<TestDevice> devices = userSteps.onTestDevicesSteps().getDevicesList(appId);

        assertThat("полный список тестовых устройств содержит устройство, эквивалентное ожидаемому",
                devices, hasItem(equivalentTo(expectedDevice)));
    }

    @Test
    public void checkDeviceInFilteredList() {
        final List<TestDevice> devicesOfGivenPurpose = userSteps.onTestDevicesSteps().getDevicesList(appId, param(devicePurpose));

        assertThat("список тестовых устройств определенного назначения содержит устройство, " +
                "эквивалентное ожидаемому", devicesOfGivenPurpose, hasItem(equivalentTo(expectedDevice)));
    }

    @After
    public void teardown() {
        userSteps.onTestDevicesSteps().deleteTestDeviceAndIgnoreResult(appId, addedDevice);
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

}
