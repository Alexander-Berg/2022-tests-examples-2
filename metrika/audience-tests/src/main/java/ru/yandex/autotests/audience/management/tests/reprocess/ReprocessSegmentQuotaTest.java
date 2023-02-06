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

import static ru.yandex.autotests.audience.errors.ManagementError.REPROCESS_QUOTA_EXCEEDED;
import static ru.yandex.autotests.audience.errors.ManagementError.REPROCESS_WRONG_TYPE;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.SEGMENTS})
@Title("Перерасчет: квота перерасчета сегментов")
public class ReprocessSegmentQuotaTest {
    private static final User OWNER = Users.USER_FOR_LOOKALIKE;
    private static final UserSteps user = UserSteps.withUser(OWNER);
    private static final int segmentQuota = 2;

    @Test
    public void reprocessSegmentQuotaTest() {
        user.onSegmentsSteps().reprocessSegment(TestData.SEGMENT_FOR_REPROCESS_QUOTA);
        for (int i = 0; i < segmentQuota - 1; i++) {
            user.onSegmentsSteps().reprocessSegmentAndExpectError(REPROCESS_WRONG_TYPE, TestData.SEGMENT_FOR_REPROCESS_QUOTA);
        }
        user.onSegmentsSteps().reprocessSegmentAndExpectError(REPROCESS_QUOTA_EXCEEDED, TestData.SEGMENT_FOR_REPROCESS_QUOTA);
    }
}
