package ru.yandex.autotests.audience.management.tests.segments.geo.circle;

import com.google.common.collect.ImmutableList;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.geo.GeoSegment;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

/**
 * Created by ava1on on 28.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.GEO
})
@Title("Геосегменты: изменение сегмента с типом «геолокация» (негативные тесты)")
@RunWith(Parameterized.class)
public class EditGeoSegmentNegativeTest {
    private static final UserSteps user = UserSteps.withUser(SIMPLE_USER_2);

    private static GeoSegment segment;
    private GeoSegment segmentToChange;

    @Parameter
    public String description;

    @Parameter(1)
    public String newName;

    @Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                getEmptySegmentNameParams(),
                getTooLongSegmentNameParams(),
                getNullSegmentNameParams()
        );
    }

    @BeforeClass
    public static void init() {
        segment = user.onSegmentsSteps().createGeo(getGeoCircleSegment(GeoSegmentType.REGULAR));
    }

    @Before
    public void setup() {
        segmentToChange = getSegmentToChange(segment, newName);
    }

    @Test
    public void checkTryEditGeoSegment() {
        user.onSegmentsSteps().editSegmentAndExpectError(error, segment.getId(), segmentToChange);
    }

    @AfterClass
    public static void cleanUp() {
        user.onSegmentsSteps().deleteSegment(segment.getId());
    }
}
