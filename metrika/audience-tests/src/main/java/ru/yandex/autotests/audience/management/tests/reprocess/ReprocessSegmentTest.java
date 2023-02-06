package ru.yandex.autotests.audience.management.tests.reprocess;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.SegmentExternalStatus;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.data.users.Users;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;
import java.util.Objects;
import java.util.Optional;

import static ru.yandex.autotests.audience.management.tests.TestData.SEGMENT_FOR_REPROCESS;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.*;
import static org.hamcrest.Matchers.*;


@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.SEGMENTS})
@Title("Перерасчет: перерасчет сегментов")
public class ReprocessSegmentTest {
    private static final User OWNER = Users.USER_FOR_LOOKALIKE;
    private static final UserSteps user = UserSteps.withUser(OWNER);
    private static final Long segmentId = SEGMENT_FOR_REPROCESS;

    @Before
    public void setup() {
        BaseSegment segment = getSegmentUnderTest();
        assumeThat("сегмент в статусе processed_fully", segment.getStatus(), is(SegmentExternalStatus.PROCESSED));
    }

    @Test
    public void testReprocess() {
        user.onSegmentsSteps().reprocessSegment(segmentId);
        BaseSegment modifiedSegment = getSegmentUnderTest();
        assertThat("статус поменялся на updated", modifiedSegment.getStatus(), is(SegmentExternalStatus.IS_UPDATED));
    }

    private BaseSegment getSegmentUnderTest() {
        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();
        Optional<BaseSegment> segmentToReprocess = segments.stream().filter(s -> Objects.equals(s.getId(), segmentId)).findFirst();
        assumeThat("сегмент существует", segmentToReprocess.isPresent(), is(true));
        return segmentToReprocess.get();
    }
}
