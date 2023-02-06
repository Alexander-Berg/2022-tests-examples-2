package ru.yandex.autotests.audience.management.tests.segments.lookalike;

import com.google.common.collect.ImmutableList;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.LookalikeSegment;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_LOOKALIKE;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

/**
 * Created by ava1on on 21.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.LAL
})
@Title("Lookalike: редактирование сегмента с типом «lookalike» (негативные тесты)")
@RunWith(Parameterized.class)
public class EditLookalikeSegmentNegativeTest {
    private static final UserSteps user = UserSteps.withUser(USER_FOR_LOOKALIKE);

    private static LookalikeSegment createdSegment;
    private static Long segmentId;

    private LookalikeSegment segmentToChange;

    @Parameter
    public String name;

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
        createdSegment = user.onSegmentsSteps().createLookalike(getLookalikeSegment());
        segmentId = createdSegment.getId();
    }

    @Before
    public void setup() {
        segmentToChange = getSegmentToChange(createdSegment, newName);
    }

    @Test
    public void checkTryEditLookalikeSegment() {
        user.onSegmentsSteps().editSegmentAndExpectError(error, segmentId, segmentToChange);
    }

    @AfterClass
    public static void cleanUp() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
