package ru.yandex.autotests.audience.management.tests.roles;

import org.junit.Test;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.steps.UserSteps;

import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_LOOKALIKE;
import static ru.yandex.autotests.audience.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;

/**
 * Created by ava1on on 17.07.17.
 */
public class GetSegmentsListNegativeTest {
    private final UserSteps user = UserSteps.withUser(SIMPLE_USER);
    private final User targetUser = USER_FOR_LOOKALIKE;

    @Test
    public void checkTryGetSegmentsList() {
        user.onSegmentsSteps().getSegmentsAndExpectError(ACCESS_DENIED, ulogin(targetUser));
    }
}
