package ru.yandex.autotests.audience.management.tests.stat;

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

import static ru.yandex.autotests.audience.data.users.User.METRIKA_COUNTER_ID;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_LOOKALIKE;
import static ru.yandex.autotests.audience.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.audience.management.tests.TestData.getGeoCircleSegment;

/**
 * Created by ava1on on 09.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.SEGMENTS,})
@Title("Статистика: получение статистики (негативные тесты)")
public class GetStatNegativeTest {
    private final User owner = SIMPLE_USER;
    private final UserSteps userOwner = UserSteps.withUser(owner);
    private final UserSteps user = UserSteps.withUser(USER_FOR_LOOKALIKE);

    private Long segmentId;

    @Before
    public void setup() {
        segmentId = userOwner.onSegmentsSteps().createGeo(getGeoCircleSegment(GeoSegmentType.LAST)).getId();
    }

    @Test
    public void checkNotAccesibleSegmentStat() {
        user.onSegmentsSteps().getStatAndExpectError(ACCESS_DENIED, segmentId);
    }

    @Test
    public void checkNoAccessToExtendedStat() {
        userOwner.onSegmentsSteps().saveGoals(segmentId, owner.get(METRIKA_COUNTER_ID), null);

        user.onSegmentsSteps().getStatAndExpectError(ACCESS_DENIED, segmentId);
    }

    @After
    public void tearDown() {
        userOwner.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
