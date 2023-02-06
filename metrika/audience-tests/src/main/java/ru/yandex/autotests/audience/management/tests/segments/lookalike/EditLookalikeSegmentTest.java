package ru.yandex.autotests.audience.management.tests.segments.lookalike;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.LookalikeSegment;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_LOOKALIKE;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 21.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.LAL
})
@Title("Lookalike: редактирование сегмента с типом «lookalike»")
public class EditLookalikeSegmentTest {
    private final UserSteps user = UserSteps.withUser(USER_FOR_LOOKALIKE);

    private LookalikeSegment createdSegment;
    private Long segmentId;
    private LookalikeSegment segmentToChange;
    private LookalikeSegment editedSegment;

    @Before
    public void setup() {
        createdSegment = user.onSegmentsSteps().createLookalike(getLookalikeSegment());
        segmentId = createdSegment.getId();
    }

    @Test
    public void checkEditedSegment() {
        segmentToChange = getSegmentToChange(createdSegment, getName(LOOKALIKE_SEGMENT_NAME_PREFIX));
        editedSegment = user.onSegmentsSteps().editSegment(segmentId, segmentToChange);

        assertThat("измененный сегмент эквивалентен изменяемому", editedSegment,
                equivalentTo(segmentToChange));
    }

    @Test
    public void checkBoundaryNameLengthEditedSegment() {
        segmentToChange = getSegmentToChange(createdSegment, BOUNDARY_LENGTH_SEGMENT_NAME);
        editedSegment = user.onSegmentsSteps().editSegment(segmentId, segmentToChange);

        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("измененный сегмент эквивалентен изменяемому", segments,
                hasBeanEquivalent(LookalikeSegment.class, segmentToChange));
    }

    @After
    public void tearDown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
