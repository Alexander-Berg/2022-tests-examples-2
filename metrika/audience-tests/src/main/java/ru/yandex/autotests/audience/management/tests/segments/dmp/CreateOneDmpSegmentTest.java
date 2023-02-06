package ru.yandex.autotests.audience.management.tests.segments.dmp;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.dmp.DmpSegment;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.audience.pubapi.SegmentRequestDmp;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.data.wrappers.SegmentRequestDmpWrapper.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 01.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.DMP
})
@Title("Dmp: создание одного сегмента с типом «dmp»")
public class CreateOneDmpSegmentTest {
    private final UserSteps user = UserSteps.withUser(SIMPLE_USER_2);

    private SegmentRequestDmp segmentRequest;
    private Long segmentId;

    @Before
    public void setup() {
        segmentRequest = getDmpSegment(DMP_SEGMENTS_IDS.get("CreateOneDmpSegmentTest"));
        segmentId = user.onSegmentsSteps().createDmp(wrap(segmentRequest)).getId();
    }

    @Test
    public void checkSegmentsInList() {
        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("сегмент присутствует в списке", segments,
                hasBeanEquivalent(DmpSegment.class, getExpectedSegment(segmentRequest)));
    }

    @After
    public void tearDown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
