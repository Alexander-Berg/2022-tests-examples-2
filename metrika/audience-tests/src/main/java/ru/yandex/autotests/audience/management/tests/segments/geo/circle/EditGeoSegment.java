package ru.yandex.autotests.audience.management.tests.segments.geo.circle;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.geo.CircleGeoSegment;
import ru.yandex.audience.geo.GeoSegment;
import ru.yandex.audience.geo.GeoSegmentType;
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
import static ru.yandex.autotests.audience.management.tests.TestData.GEO_SEGMENT_NAME_PREFIX;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by konkov on 31.03.2017.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.GEO
})
@Title("Cегменты: изменение сегмента с типом «геолокация»")
public class EditGeoSegment {
    private static final User OWNER = Users.SIMPLE_USER_2;

    private final UserSteps user = UserSteps.withUser(OWNER);

    private Long segmentId;
    private CircleGeoSegment changedSegment;
    private CircleGeoSegment expectedSegment;

    @Before
    public void setup() {
        CircleGeoSegment createdSegment = user.onSegmentsSteps().createGeo(TestData.getGeoCircleSegment(GeoSegmentType.CONDITION));
        segmentId = createdSegment.getId();

        CircleGeoSegment segmentToChange = TestData.getSegmentToChange(createdSegment,
                TestData.getName(GEO_SEGMENT_NAME_PREFIX),
                GeoSegmentType.LAST, 1L, 2L, 3L);

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
                hasBeanEquivalent(CircleGeoSegment.class, expectedSegment));
    }

    @After
    public void teardown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }

}
