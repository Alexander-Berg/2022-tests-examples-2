package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.testdevice;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.actions.EditAction;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.TestDeviceWrapper;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.TestDevice;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static org.hamcrest.CoreMatchers.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.*;
import static ru.yandex.metrika.mobmet.model.TestDevicePurpose.PUSH_NOTIFICATIONS;
import static ru.yandex.metrika.mobmet.model.TestDevicePurpose.REATTRIBUTION;
import static ru.yandex.metrika.mobmet.model.TestDeviceType.GOOGLE_AID;
import static ru.yandex.metrika.mobmet.model.TestDeviceType.IOS_IFA;

/**
 * Created by graev on 18/01/2017.
 */

@Features(Requirements.Feature.Management.TEST_DEVICES)
@Stories({
        Requirements.Story.TestDevices.EDIT,
        Requirements.Story.TestDevices.LIST
})
@Title("Редактирование тестового устройства")
@RunWith(Parameterized.class)
public final class EditTestDeviceTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private static final UserSteps userSteps = UserSteps.onTesting(OWNER);

    @Parameterized.Parameter
    public TestDeviceWrapper deviceToAdd;

    @Parameterized.Parameter(1)
    public EditAction<TestDevice, TestDevice> editAction;

    private TestDevice expectedDevice;

    private Long appId;

    private TestDeviceWrapper addedDevice;

    private TestDevice editedDevice;

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(new TestDeviceWrapper(testDevice(REATTRIBUTION, GOOGLE_AID)))
                .values(changeTestDeviceName(), changeTestDeviceId(), changeTestDevicePurpose(PUSH_NOTIFICATIONS),
                        changeTestDeviceType(IOS_IFA))
                .build();
    }

    @Before
    public void setup() {
        Application application = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = application.getId();

        addedDevice = new TestDeviceWrapper(userSteps.onTestDevicesSteps().createTestDevice(appId, deviceToAdd));

        editedDevice = userSteps.onTestDevicesSteps().updateTestDevice(appId,
                new TestDeviceWrapper(editAction.getUpdate(addedDevice.get())));

        expectedDevice = editAction.edit(addedDevice.get());
    }

    @Test
    public void checkDeviceInfo() {
        assertThat("отредактированное тестовое устройство эквивалентно ожидаемому", editedDevice,
                equivalentTo(expectedDevice));
    }

    @Test
    public void checkDeviceInList() {
        final List<TestDevice> devices = userSteps.onTestDevicesSteps().getDevicesList(appId);

        assertThat("полный список тестовых устройств содержит устройство, эквивалентное ожидаемому",
                devices, hasItem(equivalentTo(expectedDevice)));
    }

    @After
    public void teardown() {
        userSteps.onTestDevicesSteps().deleteTestDeviceAndIgnoreResult(appId, addedDevice);
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }



}
