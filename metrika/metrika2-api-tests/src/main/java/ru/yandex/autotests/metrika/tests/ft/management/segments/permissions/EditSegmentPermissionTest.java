package ru.yandex.autotests.metrika.tests.ft.management.segments.permissions;

import org.junit.AfterClass;
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
@Title("Изменение сегмента другими пользователями")
public class EditSegmentPermissionTest {
    private static UserSteps user;
    private static UserSteps userWithPermission;
    private static UserSteps userWithoutPermission;

    private static User restrictedUserWithPermission = SIMPLE_USER;
    private static User restrictedUserWithoutPermission = Users.SIMPLE_USER2;

    private static Long counterId;
    private Long segmentId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();
        userWithPermission = new UserSteps().withUser(restrictedUserWithPermission);
        userWithoutPermission = new UserSteps().withUser(restrictedUserWithoutPermission);

        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounterWithEditPermission(restrictedUserWithPermission)).getId();
    }

    @Before
    public void setup() {
        segmentId = user.onManagementSteps().onSegmentsSteps()
                .createSegmentAndExpectSuccess(counterId, getDefaultSegment()).getSegmentId();
    }

    @Test
    public void editSegmentWithPermissionTest() {
        userWithPermission.onManagementSteps().onSegmentsSteps()
                .editSegmentAndExpectSuccess(counterId, segmentId, getDefaultSegment());
    }

    @Test
    public void editSegmentWithoutPermissionTest() {
        userWithoutPermission.onManagementSteps().onSegmentsSteps()
                .editSegmentAndExpectError(ACCESS_DENIED, counterId, segmentId, getDefaultSegment());
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
