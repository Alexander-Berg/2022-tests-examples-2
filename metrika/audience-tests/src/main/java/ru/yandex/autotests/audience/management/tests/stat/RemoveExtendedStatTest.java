package ru.yandex.autotests.audience.management.tests.stat;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.audience.data.users.User.METRIKA_COUNTER_ID;
import static ru.yandex.autotests.audience.data.users.User.METRIKA_GOALS_IDS;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.management.tests.TestData.getGeoCircleSegment;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 08.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.SEGMENTS,})
@Title("Статистика: удаление расширенной статистики")
public class RemoveExtendedStatTest {
    private static final User OWNER = SIMPLE_USER;
    private static final UserSteps user = UserSteps.withUser(OWNER);

    private static Long segmentId;
    private static List<Long> goalIds;

    @BeforeClass
    public static void setup() {
        segmentId = user.onSegmentsSteps().createGeo(getGeoCircleSegment(GeoSegmentType.LAST)).getId();
        Long counterId = OWNER.get(METRIKA_COUNTER_ID);
        goalIds= OWNER.get(METRIKA_GOALS_IDS);
        user.onSegmentsSteps().saveGoals(segmentId, counterId, goalIds);

        user.onSegmentsSteps().saveGoals(segmentId, null, null);
    }

    @Test
    public void checkExtendedStatCounter() {
        Long counter = user.onSegmentsSteps().getStat(segmentId).getSettings().getCounterId();

        assertThat("в статистике отсутствует счетчик", counter, equalTo(null));
    }

    @Test
    public void checkExtendedStatGoals() {
        List<Long> goals = user.onSegmentsSteps().getStat(segmentId).getSettings().getGoals();

        assertThat("в статистике отсутствуют цели", goals, empty());
    }

    @AfterClass
    public static void cleanUp() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
