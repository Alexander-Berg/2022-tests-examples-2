package ru.yandex.autotests.audience.management.tests.segments.metrika;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.MetrikaSegmentType;
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
import static ru.yandex.autotests.audience.management.tests.TestData.getMetrikaSegment;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 25.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.APPMETRICA
})
@Title("Metrika: удаление сегмента с типом «Metrika»")
public class DeleteMetrikaSegmentTest {
    private final User owner = Users.SIMPLE_USER;
    private final UserSteps user = UserSteps.withUser(owner);

    private Long segmentId;

    @Before
    public void setup() {
        segmentId = user.onSegmentsSteps().createMetrika(getMetrikaSegment(MetrikaSegmentType.COUNTER_ID, owner)).getId();

        user.onSegmentsSteps().deleteSegment(segmentId);
    }

    @Test
    public void checkSegmentDeleted() {
        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("сегмент отсутствует в списке", segments,
                not(hasItem(having(on(BaseSegment.class).getId(), equalTo(segmentId)))));
    }
}
