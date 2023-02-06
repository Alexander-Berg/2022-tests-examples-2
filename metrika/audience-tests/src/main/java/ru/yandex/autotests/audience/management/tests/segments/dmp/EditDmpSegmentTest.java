package ru.yandex.autotests.audience.management.tests.segments.dmp;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.dmp.DmpSegment;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.data.wrappers.SegmentRequestDmpWrapper.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 02.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.DMP
})
@Title("Dmp: изменение сегмента с типом «dmp»")
public class EditDmpSegmentTest {
    private static final UserSteps user = UserSteps.withUser(SIMPLE_USER_2);

    private static DmpSegment createdSegment;
    private static Long segmentId;

    private DmpSegment segmentToChange;
    private DmpSegment editedSegment;

    @BeforeClass
    public static void init() {
        createdSegment = user.onSegmentsSteps().createDmp(wrap(getDmpSegment(DMP_SEGMENTS_IDS.get("EditDmpSegmentTest"))));
        segmentId = createdSegment.getId();
    }

    @Test
    public void checkEditedSegment() {
        segmentToChange = getSegmentToChange(createdSegment, getName(DMP_SEGMENT_PREFIX));
        editedSegment = user.onSegmentsSteps().editSegment(segmentId, segmentToChange);

        assertThat("измененный сегмент эквивалентен изменяемому", editedSegment,
                equivalentTo(segmentToChange));
    }

    @Test
    public void checkBoundarySegmentNameLength() {
        segmentToChange = getSegmentToChange(createdSegment, BOUNDARY_LENGTH_SEGMENT_NAME);
        editedSegment = user.onSegmentsSteps().editSegment(segmentId, segmentToChange);

        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("измененный сегмент эквивлентен изменяемому", segments,
                hasBeanEquivalent(DmpSegment.class, segmentToChange));
    }

    @AfterClass
    public static void cleanUp() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
