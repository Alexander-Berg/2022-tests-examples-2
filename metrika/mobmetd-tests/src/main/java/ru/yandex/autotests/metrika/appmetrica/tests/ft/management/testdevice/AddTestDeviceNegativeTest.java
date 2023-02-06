package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.testdevice;

import java.util.Collection;

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
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.TestDeviceType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.TEST_DEVICE_PUSH_ONLY_PURPOSE_CONFLICT;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.testDevice;
import static ru.yandex.metrika.mobmet.model.TestDevicePurpose.REATTRIBUTION;
import static ru.yandex.metrika.mobmet.model.TestDeviceType.APPMETRICA_DEVICE_ID;
import static ru.yandex.metrika.mobmet.model.TestDeviceType.HUAWEI_OAID;
import static ru.yandex.metrika.mobmet.model.TestDeviceType.IOS_IFV;

@Features(Requirements.Feature.Management.TEST_DEVICES)
@Stories({
        Requirements.Story.TestDevices.ADD,
        Requirements.Story.TestDevices.LIST
})
@Title("Добавление тестового устройства (негативный)")
@RunWith(Parameterized.class)
public class AddTestDeviceNegativeTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private static final UserSteps userSteps = UserSteps.onTesting(OWNER);

    @Parameterized.Parameter
    public TestDeviceType deviceType;

    private Long appId;

    private TestDeviceWrapper addedDevice;

    @Parameterized.Parameters(name = "Тип={0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(new Object[]{APPMETRICA_DEVICE_ID})
                .add(new Object[]{IOS_IFV})
                .add(new Object[]{HUAWEI_OAID})
                .build();
    }

    @Before
    public void setup() {
        Application application = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = application.getId();
    }

    @Test
    public void checkAddDeviceFails() {
        TestDeviceWrapper deviceToAdd = new TestDeviceWrapper(testDevice(REATTRIBUTION, deviceType));
        addedDevice = new TestDeviceWrapper(userSteps.onTestDevicesSteps()
                .createTestDeviceAndExpectError(appId, deviceToAdd, TEST_DEVICE_PUSH_ONLY_PURPOSE_CONFLICT));
    }

    @After
    public void teardown() {
        userSteps.onTestDevicesSteps().deleteTestDeviceAndIgnoreResult(appId, addedDevice);
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
