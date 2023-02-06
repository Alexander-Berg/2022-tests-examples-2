package ru.yandex.autotests.audience.management.tests.segments.dmp;

import com.google.common.collect.ImmutableList;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.dmp.DmpSegment;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.data.wrappers.SegmentRequestDmpWrapper.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

/**
 * Created by ava1on on 02.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.DMP
})
@Title("Dmp: изменение сегмента с типом «dmp» (негативные тесты)")
@RunWith(Parameterized.class)
public class EditDmpSegmentNegativeTest {
    private static final UserSteps user = UserSteps.withUser(SIMPLE_USER_2);

    private static DmpSegment createdSegment;
    private static Long segmentId;

    private DmpSegment segmentToChange;

    @Parameter
    public String description;

    @Parameter(1)
    public String newName;

    @Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                getEmptySegmentNameParams(),
                getTooLongSegmentNameParams(),
                getNullSegmentNameParams()
        );
    }

    @BeforeClass
    public static void init() {
        createdSegment = user.onSegmentsSteps()
                .createDmp(wrap(getDmpSegment(DMP_SEGMENTS_IDS.get("EditDmpSegmentNegativeTest"))));
        segmentId = createdSegment.getId();
    }

    @Before
    public void setup() {
        segmentToChange = getSegmentToChange(createdSegment, newName);
    }

    @Test
    public void checkTryEditDmpSegment() {
        user.onSegmentsSteps().editSegmentAndExpectError(error, segmentId, segmentToChange);
    }

    @AfterClass
    public static void cleanUp() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
