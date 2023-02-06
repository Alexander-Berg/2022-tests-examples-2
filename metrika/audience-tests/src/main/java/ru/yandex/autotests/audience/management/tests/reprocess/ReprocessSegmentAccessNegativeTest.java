package ru.yandex.autotests.audience.management.tests.reprocess;

import org.junit.Test;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.data.users.Users;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.audience.errors.ManagementError.ACCESS_DENIED;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.SEGMENTS})
@Title("Перерасчет: доступ на перерасчет сегментов")
public class ReprocessSegmentAccessNegativeTest {

    private static final User OWNER = Users.SIMPLE_USER;
    private static final UserSteps user = UserSteps.withUser(OWNER);

    @Test
    public void reprocessSegmentQuotaTest() {
        user.onSegmentsSteps().reprocessSegmentAndExpectError(ACCESS_DENIED, TestData.SEGMENT_FOR_REPROCESS_QUOTA);
    }

}
