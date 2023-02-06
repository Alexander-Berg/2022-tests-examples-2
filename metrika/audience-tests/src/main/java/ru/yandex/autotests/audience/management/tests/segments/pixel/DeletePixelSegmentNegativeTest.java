package ru.yandex.autotests.audience.management.tests.segments.pixel;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.SegmentType;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.audience.data.users.Users.SUPER_USER;
import static ru.yandex.autotests.audience.errors.ManagementError.HAS_DEPENDENT_SEGMENTS;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;

/**
 * Created by ava1on on 25.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.PIXEL
})
@Title("Пиксель: удаление сегмента с типом «pixel» (негативные тесты)")
public class DeletePixelSegmentNegativeTest {
    private final UserSteps user = UserSteps.withUser(SUPER_USER);

    private Long segmentId;

    @Before
    public void setup() {
        segmentId = user.onSegmentsSteps()
                .createLookalike(getLookalikeSegment(SEGMENTS.get(SegmentType.PIXEL)), ulogin(PIXEL_SEGMENT_OWNER))
                .getId();
    }

    @Test
    public void checkTryDeleteSegmentWithDependent() {
        user.onSegmentsSteps().deleteSegmentAndExpectError(HAS_DEPENDENT_SEGMENTS, SEGMENTS.get(SegmentType.PIXEL));
    }

    @After
    public void tearDown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
