package ru.yandex.autotests.audience.management.tests.stat;

import com.google.common.collect.ImmutableList;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.audience.data.users.User.*;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.errors.ManagementError.*;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

/**
 * Created by ava1on on 08.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.SEGMENTS,})
@Title("Статистика: настройка расширенной статистики (негативные тесты)")
@RunWith(Parameterized.class)
public class SetExtendedStatNegativeTest {
    private static final User OWNER = SIMPLE_USER;
    private static final UserSteps user = UserSteps.withUser(OWNER);

    private static Long segmentId;

    @Parameter
    public String description;

    @Parameter(1)
    public Long counterId;

    @Parameter(2)
    public List<Long> goalIds;

    @Parameter(3)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {3}")
    public static Collection<Object[]> createParameters() {
        Long counter = OWNER.get(METRIKA_COUNTER_ID);
        List<Long> moreGoals = ImmutableList.<Long>builder()
                .addAll(OWNER.get(METRIKA_GOALS_IDS))
                .add(OWNER.get(METRIKA_GOAL_ID))
                .build();

        return ImmutableList.of(
                createStatNegativeParams("пустой counter", null, OWNER.get(METRIKA_GOALS_IDS),
                        STAT_COUNTER_IS_ABSENT),
                createStatNegativeParams("нет доступа к счетчику", NOT_ACCESSIBLE_METRIKA_COUNTER, null,
                        ACCESS_DENIED_FOR_COUNTER),
                createStatNegativeParams("цель от другого счетчика", counter,
                        OWNER.get(ANOTHER_COUNTER_GOAL_IDS), STAT_GOAL_FROM_ANOTHER_COUNTER),
                createStatNegativeParams("нет доступа к цели", counter, NOT_ACCESSIBLE_GOAL,
                        STAT_GOAL_FROM_ANOTHER_COUNTER),
                createStatNegativeParams("больше 3 целей", counter, moreGoals, MORE_THAN_3_GOALS)
        );
    }

    @BeforeClass
    public static void setup() {
        segmentId = user.onSegmentsSteps().createGeo(getGeoCircleSegment(GeoSegmentType.CONDITION)).getId();
    }

    @Test
    public void checkTryCreateExtendedStat() {
        user.onSegmentsSteps().saveGoalsAndExpectError(error, segmentId, counterId, goalIds);
    }

    @AfterClass
    public static void tearDown() {
        user.onSegmentsSteps().deleteSegment(segmentId);
    }
}
