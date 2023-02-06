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
        Requirements.Story.Segments.EDIT,
        Requirements.Story.Segments.LIST,
})
@Title("Редактирование сегмента")
public class EditSegmentTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps user = UserSteps.onTesting(OWNER);

    private MobSegment expectedSegment;

    private MobSegment updatedSegment;

    private Long appId;

    private Long segmentId;

    @Before
    public void setup() {
        final MobSegment segmentToAdd = defaultSegment();

        final Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        segmentId = user.onSegmentSteps().addSegment(appId, segmentToAdd).getSegmentId();


        final String updateValue = "update";
        MobSegment segmentToUpdate = new MobSegment()
                .withName(getTestSegmentName())
                .withParams(defaultSegmentParams(updateValue));
        updatedSegment = user.onSegmentSteps().updateSegment(appId, segmentId, segmentToUpdate);
        expectedSegment = copy(updatedSegment).withExpression(defaultSegmentExpression(updateValue));
    }

    @Test
    public void addSegment() {
        assertThat("обновлённый сегмент эквивалентен ожидаемому", updatedSegment, equivalentTo(expectedSegment));
    }

    @Test
    public void segmentShouldBeInSegmentsList() {
        final List<MobSegment> segments = user.onSegmentSteps().getSegmentsList(appId);
        assertThat("список сегментов содержит сегмент, эквивалентный ожидаемому", segments,
                hasItem(equivalentTo(expectedSegment)));
    }

    @After
    public void teardown() {
        user.onSegmentSteps().deleteSegmentAndIgnoreResult(appId, segmentId);
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
