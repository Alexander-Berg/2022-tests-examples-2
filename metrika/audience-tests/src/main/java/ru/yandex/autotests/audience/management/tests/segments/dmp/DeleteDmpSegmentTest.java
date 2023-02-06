package ru.yandex.autotests.audience.management.tests.segments.dmp;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.data.wrappers.SegmentRequestDmpWrapper.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.DMP_SEGMENTS_IDS;
import static ru.yandex.autotests.audience.management.tests.TestData.getDmpSegment;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 02.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.DMP
})
@Title("Dmp: удаление сегмента с типом «dmp»")
public class DeleteDmpSegmentTest {
    private final UserSteps user = UserSteps.withUser(SIMPLE_USER_2);

    private Long segmentId;

    @Before
    public void setup() {
        segmentId = user.onSegmentsSteps().createDmp(
                wrap(getDmpSegment(DMP_SEGMENTS_IDS.get("DeleteDmpSegmentTest")))).getId();

        user.onSegmentsSteps().deleteSegment(segmentId);
    }

    @Test
    public void checkDeleteDmpSegment() {
        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("удаленный сегмент отсутствует в списке", segments,
                not(hasItem(having(on(BaseSegment.class), equalTo(segmentId)))));
    }
}
