package ru.yandex.autotests.audience.management.tests.segments.geo.circle;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.SegmentType;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_LOOKALIKE;
import static ru.yandex.autotests.audience.errors.ManagementError.HAS_DEPENDENT_SEGMENTS;
import static ru.yandex.autotests.audience.management.tests.TestData.SEGMENTS;
import static ru.yandex.autotests.audience.management.tests.TestData.getLookalikeSegment;

/**
 * Created by ava1on on 25.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.GEO
})
@Title("Геосегменты: удаление сегмента с типом «геолокация» (негативные тесты)")
public class DeleteGeoSegmentNegativeTest {
    private final UserSteps user = UserSteps.withUser(USER_FOR_LOOKALIKE);

    private Long segmentId;

    @Before
    public void setup() {
        segmentId = user.onSegmentsSteps().createLookalike(getLookalikeSegment(SEGMENTS.get(SegmentType.GEO)))
                .getId();
    }

    @Test
    public void checkTryDeleteSegmentWithDependent() {
        user.onSegmentsSteps().deleteSegmentAndExpectError(HAS_DEPENDENT_SEGMENTS, SEGMENTS.get(SegmentType.GEO));
    }

    @After
    public void tearDown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
