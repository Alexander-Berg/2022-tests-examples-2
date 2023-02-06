package ru.yandex.autotests.audience.management.tests.segments.geo.polygon;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.management.tests.TestData.getGeoPolygonSegment;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.GEO
})
@Title("Геосегменты: удаление сегмента с типом «геолокация - полигоны»")
public class DeleteGeoSegmentTest {
    private final UserSteps user = UserSteps.withUser(SIMPLE_USER_2);

    private Long segmentId;

    @Before
    public void setup() {
        segmentId = user.onSegmentsSteps().createGeo(getGeoPolygonSegment(GeoSegmentType.REGULAR))
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
