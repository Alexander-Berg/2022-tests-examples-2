package ru.yandex.autotests.audience.management.tests.stat;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.isIn;
import static ru.yandex.autotests.audience.data.users.User.*;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.management.tests.TestData.getGeoCircleSegment;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 06.07.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.SEGMENTS,})
@Title("Статистика: изменение расширенной статистики")
public class EditExtendedStatTest {
    private final User owner = SIMPLE_USER;
    private final UserSteps user = UserSteps.withUser(owner);

    private Long segmentId;
    private List<Long> goals = ImmutableList.of(owner.get(METRIKA_GOAL_ID));

    @Before
    public void setup() {
        segmentId = user.onSegmentsSteps().createGeo(getGeoCircleSegment(GeoSegmentType.CONDITION)).getId();
        user.onSegmentsSteps().saveGoals(segmentId, owner.get(METRIKA_COUNTER_ID), owner.get(METRIKA_GOALS_IDS));

        user.onSegmentsSteps().saveGoals(segmentId, owner.get(METRIKA_COUNTER_ID), goals);
    }

    @Test
    public void checkEditExtendedStat() {
        List<Long> goalIds = user.onSegmentsSteps().getStat(segmentId).getSettings().getGoals();

        assertThat("в статистике указаны ожидаемые цели", goals, everyItem(isIn(goalIds)));
    }

    @After
    public void tearDown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
