package ru.yandex.autotests.audience.management.tests.segments.dmp;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.audience.data.wrappers.SegmentRequestDmpWrapper;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.data.wrappers.SegmentRequestDmpWrapper.wrap;
import static ru.yandex.autotests.audience.errors.ManagementError.INCORRECT_DMP_SEGMENT;
import static ru.yandex.autotests.audience.errors.ManagementError.NOT_NULL;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

/**
 * Created by ava1on on 01.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.DMP
})
@Title("Dmp: создание сегмента с типом «dmp» (негативные тесты")
@RunWith(Parameterized.class)
public class CreateOneDmpSegmentNegativeTest {
    private final UserSteps user = UserSteps.withUser(SIMPLE_USER_2);

    private Long segmentId;

    @Parameter
    public String description;

    @Parameter(1)
    public SegmentRequestDmpWrapper segmentRequestWrapper;

    @Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                createDmpNegativeParam("dmp сегмент в статусе deleted", createDeletedDmpSegment(),
                        INCORRECT_DMP_SEGMENT),
                createDmpNegativeParam("охват сегмента меньше 1000", createTooSmallSizeDmpSegment(),
                        INCORRECT_DMP_SEGMENT),
                createDmpNegativeParam("нет доступа до сегмента dmp", createNoAccessDmpSegment(),
                        INCORRECT_DMP_SEGMENT),
                createDmpNegativeParam("сегмент на основе dmp уже создан", createExistingDmpSegment(),
                        INCORRECT_DMP_SEGMENT),
                createDmpNegativeParam("отсутствует параметр dmp_id",
                        getDmpSegment(null, DMP_SEGMENTS_IDS.get("CreateOneDmpSegmentNegativeTest")), NOT_NULL),
                createDmpNegativeParam("отсутствует параметр dmp_segment_id",
                        getDmpSegment(DMP_ID, null), NOT_NULL)
        );
    }

    @Before
    public void setup() {
        segmentId = user.onSegmentsSteps().createDmp(wrap(createExistingDmpSegment())).getId();
    }

    @Test
    public void checkTryCreateDmpSegment() {
        user.onSegmentsSteps().createDmpAndExpectError(error, segmentRequestWrapper);
    }

    @After
    public void tearDown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
