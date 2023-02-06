package ru.yandex.autotests.audience.management.tests.segments.metrika;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.MetrikaSegmentType;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.SegmentRequestMetrika;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.audience.data.users.User.METRIKA_COUNTER_ID;
import static ru.yandex.autotests.audience.data.users.User.METRIKA_SEGMENT_ID;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.data.users.Users.USER_LOOKALIKE_NEGATIVE;
import static ru.yandex.autotests.audience.errors.ManagementError.*;
import static ru.yandex.autotests.audience.management.tests.TestData.TOO_LONG_SEGMENT_NAME_LENGTH;
import static ru.yandex.autotests.audience.management.tests.TestData.getMetrikaSegment;

/**
 * Created by ava1on on 25.10.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.METRIKA
})
@Title("Metrika: создание с типом «Metrika» (негативные тесты)")
@RunWith(Parameterized.class)
public class CreateMetrikaSegmentNegativeTest {
    private static final User WITH_ACCESS = SIMPLE_USER;
    private static final User NO_ACCESS = USER_LOOKALIKE_NEGATIVE;
    private static final UserSteps user = UserSteps.withUser(WITH_ACCESS);

    @Parameter
    public String description;

    @Parameter(1)
    public SegmentRequestMetrika segmentRequest;

    @Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                toArray("пустой name",
                        getMetrikaSegment(MetrikaSegmentType.COUNTER_ID, WITH_ACCESS).withName(StringUtils.EMPTY),
                        INCORRECT_SEGMENT_NAME_LENGTH),
                toArray("отсутствует name",
                        getMetrikaSegment(MetrikaSegmentType.SEGMENT_ID, WITH_ACCESS).withName(null),
                        NOT_NULL),
                toArray("слишком длинный name",
                        getMetrikaSegment(MetrikaSegmentType.GOAL_ID, WITH_ACCESS).withName(TOO_LONG_SEGMENT_NAME_LENGTH),
                        INCORRECT_SEGMENT_NAME_LENGTH),
                toArray("отсутствует metrika_segment_type",
                        getMetrikaSegment(MetrikaSegmentType.COUNTER_ID, WITH_ACCESS).withMetrikaSegmentType(null),
                        NOT_NULL),
                toArray("отсутствует metrika_segment_id",
                        getMetrikaSegment(MetrikaSegmentType.SEGMENT_ID, WITH_ACCESS).withMetrikaSegmentId(null),
                        NO_OBJECT),
                toArray("не совпадают type и id",
                        getMetrikaSegment(MetrikaSegmentType.GOAL_ID, WITH_ACCESS)
                                .withMetrikaSegmentId(WITH_ACCESS.get(METRIKA_COUNTER_ID)),
                        NO_OBJECT),
                toArray("нет доступа к счетчику",
                        getMetrikaSegment(MetrikaSegmentType.SEGMENT_ID, WITH_ACCESS)
                                .withMetrikaSegmentId(NO_ACCESS.get(METRIKA_SEGMENT_ID)),
                        ACCESS_DENIED_FOR_COUNTER)
        );
    }

    @Test
    public void checkCreateMetrikaSegmentNegativeTest() {
        user.onSegmentsSteps().createMetrikaAndExpectError(error, segmentRequest);
    }
}
