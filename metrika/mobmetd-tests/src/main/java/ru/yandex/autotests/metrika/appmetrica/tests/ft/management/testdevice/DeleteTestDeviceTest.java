package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.testdevice;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.ArrayUtils;
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
import ru.yandex.metrika.mobmet.model.TestDevice;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static org.hamcrest.CoreMatchers.hasItem;
import static org.hamcrest.CoreMatchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.someTestDevice;

/**
 * Created by graev on 18/01/2017.
 */
@Features(Requirements.Feature.Management.TEST_DEVICES)
@Stories({
        Requirements.Story.TestDevices.DELETE,
        Requirements.Story.TestDevices.LIST
})
@Title("Удаление тестового устройства")
@RunWith(Parameterized.class)
public final class DeleteTestDeviceTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private static final UserSteps userSteps = UserSteps.onTesting(OWNER);

    @Parameterized.Parameter
    public TestDeviceWrapper deviceToAdd;

    private TestDevice expectedDevice;

    private Long appId;

    private TestDeviceWrapper addedDevice;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param(someTestDevice())
        );
    }

    @Before
    public void setup() {
        expectedDevice = deviceToAdd.get();

        Application application = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = application.getId();

        addedDevice = new TestDeviceWrapper(userSteps.onTestDevicesSteps().createTestDevice(appId, deviceToAdd));

        userSteps.onTestDevicesSteps().deleteTestDevice(appId, addedDevice);
    }

    @Test
    public void checkDeviceNotFoundInList() {
        final List<TestDevice> devices = userSteps.onTestDevicesSteps().getDevicesList(appId);

        assertThat("список тестовых устройств не содержит устройства, эквивалентного ожидаемому",
                devices, not(hasItem(equivalentTo(expectedDevice))));
    }

    @After
    public void teardown() {
        userSteps.onTestDevicesSteps().deleteTestDeviceAndIgnoreResult(appId, addedDevice);
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(TestDevice device) {
        return ArrayUtils.toArray(new TestDeviceWrapper(device));
    }

}
