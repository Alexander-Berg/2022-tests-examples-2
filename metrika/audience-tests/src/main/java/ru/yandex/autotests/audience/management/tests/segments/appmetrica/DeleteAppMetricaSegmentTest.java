package ru.yandex.autotests.audience.management.tests.segments.appmetrica;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.AppMetricaSegmentType;
import ru.yandex.audience.BaseSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.data.users.Users;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.audience.management.tests.TestData.getAppMetricaSegment;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 25.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.APPMETRICA
})
@Title("AppMetrica: удаление сегмента с типом «AppMetrica»")
public class DeleteAppMetricaSegmentTest {
    private final User owner = Users.SIMPLE_USER;
    private final UserSteps user = UserSteps.withUser(owner);

    private Long segmentId;

    @Before
    public void setup() {
        segmentId = user.onSegmentsSteps().createAppMetrica(getAppMetricaSegment(AppMetricaSegmentType.API_KEY, owner))
                .getId();

        user.onSegmentsSteps().deleteSegment(segmentId);
    }

    @Test
    public void checkSegmentDeleted() {
        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("сегмент отсутствует в списке", segments,
                not(hasItem(having(on(BaseSegment.class).getId(), equalTo(segmentId)))));
    }
}
