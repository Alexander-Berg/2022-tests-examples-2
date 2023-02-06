package ru.yandex.autotests.audience.management.tests.segments.client.yuid;

import org.junit.After;
import org.junit.Test;

import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.audience.data.users.Users.INTERNAL_DMP_UPLOADER;
import static ru.yandex.autotests.audience.data.users.Users.INTERNAL_DMP_UPLOADER_2;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_INTERNAL_DMP;
import static ru.yandex.autotests.audience.errors.ManagementError.CLIENT_INVALID_SEGMENT;
import static ru.yandex.autotests.audience.errors.ManagementError.HAS_DEPENDENT_SEGMENTS;
import static ru.yandex.autotests.audience.management.tests.TestData.YUID_SEGMENT_FOR_LOOKALIKE;
import static ru.yandex.autotests.audience.management.tests.TestData.getLookalikeSegment;

/**
 * Created by ava1on on 09.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.INTERNAL_DMP
})
@Title("Internal dmp: удаление сегмента с типом «yuid» (негативные тесты)")
public class DeleteYuidSegmentNegativeTest {
    private final UserSteps userUploader = UserSteps.withUser(INTERNAL_DMP_UPLOADER);
    private final UserSteps userWithNoAccess = UserSteps.withUser(INTERNAL_DMP_UPLOADER_2);
    private final UserSteps userOwner = UserSteps.withUser(USER_FOR_INTERNAL_DMP);

    private Long segmentId;

    @Test
    public void checkTryDeleteSegmentWithDependent() {
        segmentId = userOwner.onSegmentsSteps().createLookalike(getLookalikeSegment(YUID_SEGMENT_FOR_LOOKALIKE)).getId();

        userUploader.onSegmentsSteps().deleteClientSegmentAndExpectError(HAS_DEPENDENT_SEGMENTS, YUID_SEGMENT_FOR_LOOKALIKE);
    }

    @Test
    public void checkTryDeleteByAnotherUploader() {
        userWithNoAccess.onSegmentsSteps().deleteClientSegmentAndExpectError(CLIENT_INVALID_SEGMENT, YUID_SEGMENT_FOR_LOOKALIKE);
    }

    @After
    public void tearDown() {
        userOwner.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
