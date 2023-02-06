package ru.yandex.autotests.audience.management.tests.segments.lookalike;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.SegmentType;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;
import java.util.stream.Collectors;

import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_LOOKALIKE;
import static ru.yandex.autotests.audience.management.tests.TestData.SEGMENTS;
import static ru.yandex.autotests.audience.management.tests.TestData.getLookalikeSegment;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 24.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.LAL
})
@Title("Lookalike: удаление сегмента с типом «lookalike»")
public class DeleteLookalikeSegmentTest {
    private final UserSteps user = UserSteps.withUser(USER_FOR_LOOKALIKE);

    private Long segmentId;

    @Before
    public void setup() {
        segmentId = user.onSegmentsSteps().createLookalike(getLookalikeSegment(SEGMENTS.get(SegmentType.LOOKALIKE)))
                .getId();

        user.onSegmentsSteps().deleteSegment(segmentId);
    }

    @Test
    public void checkSegmentDeleted() {
        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("сегмент отсутствует в списке", segments.stream().map(BaseSegment::getId)
                        .collect(Collectors.toList()),
                not(hasItem(segmentId))
        );
    }
}
