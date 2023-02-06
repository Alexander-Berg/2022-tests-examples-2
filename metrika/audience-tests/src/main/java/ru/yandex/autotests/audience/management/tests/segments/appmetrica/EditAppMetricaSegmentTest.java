package ru.yandex.autotests.audience.management.tests.segments.appmetrica;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.AppMetricaSegment;
import ru.yandex.audience.AppMetricaSegmentType;
import ru.yandex.audience.BaseSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.data.users.Users;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ru.yandex.autotests.audience.data.wrappers.WrapperBase.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.APPMETRICA_SEGMENT_NAME_PREFIX;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by konkov on 31.03.2017.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.APPMETRICA
})
@Title("Cегменты: изменение сегмента из объекта AppMetrica")
public class EditAppMetricaSegmentTest {
    private static final User OWNER = Users.USER_FOR_LOOKALIKE;

    private final UserSteps user = UserSteps.withUser(OWNER);

    private Long segmentId;
    private AppMetricaSegment changedSegment;
    private AppMetricaSegment expectedSegment;

    @Before
    public void setup() {
        AppMetricaSegment createdSegment = user.onSegmentsSteps().createAppMetrica(TestData.getAppMetricaSegment(
                AppMetricaSegmentType.API_KEY, OWNER));
        segmentId = createdSegment.getId();

        AppMetricaSegment segmentToChange = TestData.getSegmentToChange(createdSegment,
                TestData.getName(APPMETRICA_SEGMENT_NAME_PREFIX),
                AppMetricaSegmentType.SEGMENT_ID, 0L);

        changedSegment = user.onSegmentsSteps().editSegment(segmentId, segmentToChange);

        expectedSegment = wrap(createdSegment).getClone().withName(segmentToChange.getName());
    }

    @Test
    public void checkChangedSegment() {
        assertThat("измененный сегмент совпадает с ожидаемым", changedSegment,
                equivalentTo(expectedSegment));
    }

    @Test
    public void checkChangedSegmentInList() {
        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("измененный сегмент присутствует в списке сегментов", segments,
                hasBeanEquivalent(AppMetricaSegment.class, expectedSegment));
    }

    @After
    public void teardown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
