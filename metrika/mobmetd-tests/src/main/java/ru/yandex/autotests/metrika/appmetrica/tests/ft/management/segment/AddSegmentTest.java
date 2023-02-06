package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.segment;


import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.dao.MobSegment;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.*;

@Features(Requirements.Feature.Management.SEGMENT)
@Stories({
        Requirements.Story.Segments.ADD,
        Requirements.Story.Segments.LIST,
})
@Title("Добавление сегмента")
public class AddSegmentTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps user = UserSteps.onTesting(OWNER);

    private MobSegment expectedSegment;

    private Long appId;

    private MobSegment addedSegment;

    @Before
    public void setup() {
        final MobSegment segmentToAdd = defaultSegment();
        expectedSegment = copy(segmentToAdd).withExpression(defaultSegmentExpression());

        final Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        addedSegment = user.onSegmentSteps().addSegment(appId, segmentToAdd);
    }

    @Test
    public void addSegment() {
        assertThat("добавленный сегмент эквивалентен ожидаемому", addedSegment, equivalentTo(expectedSegment));
    }

    @Test
    public void segmentShouldBeInSegmentsList() {
        final List<MobSegment> segments = user.onSegmentSteps().getSegmentsList(appId);
        assertThat("список сегментов содержит сегмент, эквивалентный ожидаемому", segments,
                hasItem(equivalentTo(expectedSegment)));
    }

    @After
    public void teardown() {
        user.onSegmentSteps().deleteSegmentAndIgnoreResult(appId, addedSegment.getSegmentId());
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}


