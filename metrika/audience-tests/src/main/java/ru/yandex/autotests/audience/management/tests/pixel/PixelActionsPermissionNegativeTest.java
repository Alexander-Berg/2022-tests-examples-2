package ru.yandex.autotests.audience.management.tests.pixel;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.audience.data.users.Users.*;
import static ru.yandex.autotests.audience.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.audience.management.tests.TestData.getPixelName;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;

/**
 * Created by ava1on on 26.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Роли: управление пикселем (негативные тесты)")
@RunWith(Parameterized.class)
public class PixelActionsPermissionNegativeTest {
    private final User owner = USER_DELEGATOR;
    private final UserSteps userOwner = UserSteps.withUser(owner);

    private UserSteps user;
    private Long pixelId;

    @Parameter
    public String description;

    @Parameter(1)
    public User userParam;

    @Parameterized.Parameters(name = "пользователь {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                toArray("с правом на просмотр", USER_WITH_PERM_VIEW),
                toArray("с ролью менеджер", MANAGER),
                toArray("без прав", SIMPLE_USER)
        );
    }

    @Before
    public void setup() {
        user = UserSteps.withUser(userParam);
    }

    @Test
    public void checkTryCreatePixel() {
        user.onPixelsSteps().createPixelAndAndExpectError(ACCESS_DENIED, getPixelName(), ulogin(owner));
    }

    @Test
    public void checkTryEditPixel() {
        pixelId = userOwner.onPixelsSteps().createPixel(getPixelName()).getId();

        user.onPixelsSteps().editPixelAndExpectError(ACCESS_DENIED, pixelId, getPixelName(), ulogin(owner));
    }

    @Test
    public void checkTryDeletePixel() {
        pixelId = userOwner.onPixelsSteps().createPixel(getPixelName()).getId();

        user.onPixelsSteps().deletePixelAndExpectError(ACCESS_DENIED, pixelId, ulogin(owner));
    }

    @Test
    public void checkTryRestorePixel() {
        pixelId = userOwner.onPixelsSteps().createPixel(getPixelName()).getId();
        userOwner.onPixelsSteps().deletePixel(pixelId);

        user.onPixelsSteps().restorePixelAndExpectError(ACCESS_DENIED, pixelId, ulogin(owner));
    }

    @After
    public void tearDown() {
        userOwner.onPixelsSteps().deletePixelAndIgnoreStatus(pixelId);
    }
}
