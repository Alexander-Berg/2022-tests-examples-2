package ru.yandex.autotests.metrika.tests.ft.management.segments.permissions;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithEditPermission;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultSegment;

/**
 * Created by konkov on 20.11.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Создание сегмента другими пользователями")
public class CreateSegmentPermissionTest {
    private static UserSteps user;
    private static UserSteps userWithPermission;
    private static UserSteps userWithoutPermission;

    private static User restrictedUserWithPermission = SIMPLE_USER;
    private static User restrictedUserWithoutPermission = Users.SIMPLE_USER2;

    private Long counterId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();
        userWithPermission = new UserSteps().withUser(restrictedUserWithPermission);
        userWithoutPermission = new UserSteps().withUser(restrictedUserWithoutPermission);
    }

    @Before
    public void setup() {

        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounterWithEditPermission(restrictedUserWithPermission)).getId();
    }

    @Test
    public void createSegmentWithPermissionTest() {
        userWithPermission.onManagementSteps().onSegmentsSteps().createSegmentAndExpectSuccess(
                counterId,
                getDefaultSegment());
    }

    @Test
    public void createSegmentWithoutPermissionTest() {
        userWithoutPermission.onManagementSteps().onSegmentsSteps().createSegmentAndExpectError(
                ACCESS_DENIED,
                counterId,
                getDefaultSegment());
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
